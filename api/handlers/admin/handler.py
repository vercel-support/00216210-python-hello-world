from api._lib.account import jwtAuth
from api._lib.handlers.routeable import RouteableAPIHandler


DEFAULT_RESULT_ITEMS = 100


class handler(RouteableAPIHandler):

    routes = {
        "/admin": {"get": {"handler": "dashboardGet"}},
    }

    @jwtAuth
    def dashboardGet(self):
        jsonResult = {"data": []}
        return self.write(jsonResult)
