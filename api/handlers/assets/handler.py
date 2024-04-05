from api._lib.handlers.routeable import RouteableAPIHandler


class handler(RouteableAPIHandler):

    routes = {
        "/stats": {"get": {"handler": "statsHandler"}},
    }

    def statsHandler(self):
        result = {
            "totals": [],
            "lastRegisters": [],
            "teamsLeaderboard": [],
            "countriesLeaderboard": [],
        }
        return self.write(result)
