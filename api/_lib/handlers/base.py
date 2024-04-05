import json
import traceback

from urllib.parse import urlparse, parse_qs
from http.server import BaseHTTPRequestHandler

from api._lib.model import connect_db


class HTTPException(Exception):

    API_ERRORS = {
        400: 'bad-request',
        401: 'unauthorized',
        403: 'forbiden',
        404: 'not-found',
        500: 'something-nasty'
    }

    def __init__(self, code, message=None):
        self.code = code
        self.message = message or self.API_ERRORS.get(code)


class BaseAPIHandler(BaseHTTPRequestHandler):

    urlParsed = False
    current_user = None

    def __init__(self, request, client_address, server):
        connect_db()
        BaseHTTPRequestHandler.__init__(self, request, client_address, server)

    def callSafe(self, method):
        try:
            return getattr(self, method)()

        except Exception:
            traceback.print_exc()
            return self.api_error(500)

    def do_GET(self):
        return self.callSafe('get')

    def do_POST(self):
        return self.callSafe('post')

    def do_PUT(self):
        return self.callSafe('put')

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "OPTIONS, GET, POST, PUT, DELETE")
        self.send_header(
            "Access-Control-Allow-Headers",
            "Origin, X-Requested-With, Content-Type, Accept, Authorization",
        )
        self.send_header("X-Frame-Options", "DENY")
        self.end_headers()

        return

    def _set_headers(self, code):
        self.send_response(code)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Content-type', 'application/json')
        self.end_headers()

    def api_error(self, code, responseDict=None):
        traceback.print_exc()

        self._set_headers(code)

        if responseDict:
            data = json.dumps(responseDict)
        else:
            data = json.dumps({'reason': HTTPException.API_ERRORS.get(code, 'unknown')})

        self.wfile.write(data.encode())

    def write(self, responseDict):
        try:
            data = json.dumps(responseDict)

            self._set_headers(200)
            self.wfile.write(data.encode())

        except Exception:
            return self.api_error(500)

    def get_raw_body(self):
        content_length = int(self.headers.get("Content-Length"))
        raw_body = self.rfile.read(content_length)

        return raw_body

    def get_json_body(self):
        try:
            return json.loads(self.get_raw_body())
        except Exception:
            raise HTTPException(400)

    def get_argument(self, argName, default=None):
        if not self.urlParsed:
            parsedPath = urlparse(self.path)
            self.args = parse_qs(parsedPath.query)
            self.parse_body_arguments(self.args)
            self.urlParsed = True

        ret = self.args.get(argName, default)

        if ret is None:
            raise HTTPException(400)

        if isinstance(ret, list) and len(ret) == 1:
            return ret[0]

        return ret

    def parse_body_arguments(self, arguments: dict):

        content_type = self.headers.get('Content-Type', '')

        # only parse x-www-form-urlencoded body
        if not content_type.startswith('application/x-www-form-urlencoded'):
            return

        if self.headers and 'Content-Encoding' in self.headers:
            raise HTTPException(400, 'Unsupported Content-Encoding: %s' % self.headers['Content-Encoding'])

        try:
            content_length = int(self.headers.get('Content-Length'))
            post_data = self.rfile.read(content_length)

            uri_arguments = parse_qs(post_data.decode())

        except Exception as e:
            self.log_error('Invalid x-www-form-urlencoded body: %s' % e)
            uri_arguments = {}


        for name, values in uri_arguments.items():
            if values:
                arguments.setdefault(name, []).extend(values)
