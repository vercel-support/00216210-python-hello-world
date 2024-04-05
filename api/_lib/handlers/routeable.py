import re
import traceback

from urllib.parse import urlparse, parse_qs
from api._lib.handlers.base import BaseAPIHandler, HTTPException

class RouteableAPIHandler(BaseAPIHandler):

    def callSafe(self, method):
        try:
            parsedUrl = urlparse(self.path)

            match = self.routes.get(parsedUrl.path)
            args = tuple()

            if not match:
                regex_routes = [r for r in self.routes if '([^/]+)' in r]
                for r in regex_routes:
                    compiled_route = re.compile('{}$'.format(r))
                    regex_match = compiled_route.match(parsedUrl.path)
                    if regex_match:
                        args = regex_match.groups()
                        match = self.routes.get(r)
                        break
                if not match: raise HTTPException(404)

            route_method = match.get(method)

            if route_method.get('args'):
                args = tuple(route_method['args'])

            return getattr(self, route_method['handler'])(*args)

        except HTTPException as e:
            return self.api_error(e.code)

        except Exception as e:
            traceback.print_exc()
            return self.api_error(500)