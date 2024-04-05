import re
import unicodedata
import secrets
import hashlib

# Extra characters outside of alphanumerics that we'll allow.
SLUG_OK = ""


def smart_text(s):
    return s if isinstance(s, str) else s.decode("utf-8")


def strip_accents(s):
    return "".join(
        (c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")
    )


def slugify(s, ok=SLUG_OK, lower=True, separator="-"):
    # L and N signify letter/number.
    # http://www.unicode.org/reports/tr44/tr44-4.html#GC_Values_Table
    rv = []
    for c in unicodedata.normalize("NFKC", smart_text(s)):
        cat = unicodedata.category(c)[0]
        if cat in "LN" or c in ok:
            rv.append(c)
        if cat == "Z" or c == "+":  # space
            rv.append(" ")

    new = "".join(rv).strip()
    new = re.sub("[-\s]+", separator, new)

    return new.lower() if lower else new


def static_url(resourcePath):
    return "/{}".format(resourcePath)


def gen_token(lenght=None):
    return secrets.token_hex(lenght)


def md5(txt):
    if type(txt) != bytes:
        txt = bytes(txt, "utf-8")

    m = hashlib.md5()
    m.update(txt)

    return m.hexdigest()


def sha256(str_data):
    if type(str_data) == str:
        str_data = str_data.encode()

    m = hashlib.sha256()
    m.update(str_data)

    return m.hexdigest()


def safe_div(x, y):
    if y == 0:
        return 0

    return x / y


def ordinal(n):
    return "%d%s" % (n, "tsnrhtdd"[(n / 10 % 10 != 1) * (n % 10 < 4) * n % 10 :: 4])


def sanitize(value: str, lower=True) -> str:
    return slugify(value, lower=lower, separator=" ")
