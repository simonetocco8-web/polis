import socket

from .contracts import IDENTIFIER, canonical, parse, require


class NomosUnavailable(ValueError):
    pass


class NomosClient:
    def __init__(self, socket_path, token, universe):
        require(IDENTIFIER.fullmatch(universe), "invalid_universe")
        self.socket_path = socket_path
        self._token = token
        self.universe = universe

    def _request(self, operation, data):
        with socket.socket(socket.AF_UNIX) as connection:
            connection.settimeout(10)
            connection.connect(str(self.socket_path))
            connection.sendall(canonical({"token": self._token, "universe": self.universe, "operation": operation, "data": data}))
            with connection.makefile("rb") as stream:
                raw = stream.readline(131073)
        if not raw.endswith(b"\n") or len(raw) > 131072:
            raise NomosUnavailable("nomos_unavailable")
        result = parse(raw)
        if result.get("ok") is not True:
            raise NomosUnavailable("nomos_refused")
        return result["result"]

    def view(self):
        result = self._request("archon-view", {})
        require(result["version"] == "archon-observation-1" and result["universe"] == self.universe
                and result["regime"] == "B", "invalid_observation")
        return result

    def receipt(self, key):
        return self._request("archon-receipt", {"key": key})

    def submit(self, payload):
        return self._request("submit", {"payload": payload})
