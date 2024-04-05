import json
import functools

from api._lib.model.entities import User
from jose import jwt

from hashlib import sha256

PASSWD_SALT = "A41CEBFC-F6FC-43B4-B424-B9FEB1C962A4"


class AccountInvalidException(Exception):
    pass


class AccountNotFoundException(Exception):
    pass


class AccountDuplicatedException(Exception):
    pass


def hash_passwd(plain):
    x = sha256()
    x.update(bytes(PASSWD_SALT, "utf-8"))
    x.update(bytes(plain, "utf-8"))

    return x.hexdigest()


def auth(email, password):
    user = User.objects(email=email).first()
    if not user:
        raise AccountInvalidException()

    if hash_passwd(password) != user.password:
        raise AccountInvalidException()

    return email


AUTH_REALM = "Test API"
AUTH_DOMAIN = "https://auth-domain.xxx/"
AUTH_AUDIENCE = "https://auth-audience.xxx/"
AUTH_ALGORITHM = "HS256"


def bearer_token_parse(auth):
    if auth.index("Bearer") > -1:
        return auth.split(" ")[1]


def check_token(self):
    header = self.headers.get("Authorization")
    try:
        token = bearer_token_parse(header)
        return token == "B7A73365-4BC4-4E79-B061-F5F10DE43B5E"
    except Exception:
        self.log_error("Unable to parse authentication token.")


def check_jwt(self):
    header = self.headers.get("Authorization")
    try:
        token = bearer_token_parse(header)

        payload = jwt.decode(
            token,
            PASSWD_SALT,
            algorithms=AUTH_ALGORITHM,
            audience=AUTH_AUDIENCE,
            issuer=AUTH_DOMAIN,
        )
        return User.objects.get(id=payload["sub"])

    except jwt.ExpiredSignatureError:
        self.log_error("token is expired")

    except jwt.JWTClaimsError:
        self.log_error("incorrect claims, please check the audience and issuer")

    except Exception:
        self.log_error("Unable to parse authentication token.")


def newJWT(extra):
    claims = {
        "aud": AUTH_AUDIENCE,
        "iss": AUTH_DOMAIN,
    }
    claims.update(extra)

    return jwt.encode(claims, PASSWD_SALT, algorithm=AUTH_ALGORITHM)


def jwtAuth(method):
    """Decorate methods with this to require that JWT access."""

    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        self.current_user = check_jwt(self)
        if not self.current_user:
            self.send_response(401)
            self.send_header("WWW-Authenticate", 'Bearer realm="%s" % AUTH_REALM')
            self.end_headers()
            self.wfile.write(json.dumps({"error": "unauthorized"}).encode())
            return

        return method(self, *args, **kwargs)

    return wrapper


def tokenAuth(method):
    """Decorate methods with this to require that a valid token be present in the request."""

    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        if not check_token(self):
            self.send_response(401)
            self.send_header("WWW-Authenticate", 'Bearer realm="%s" % AUTH_REALM')
            self.end_headers()
            self.wfile.write(json.dumps({"error": "unauthorized"}).encode())
            return

        return method(self, *args, **kwargs)

    return wrapper
