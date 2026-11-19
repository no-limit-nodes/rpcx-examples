"""A small, dependency-free Python client for NoLimitNodes RPCX methods.

A saved RPCX method is a JSON-RPC method called rpcx_<name> at
https://rpcx.mainnet.solana.nolimitnodes.com, with your NoLimitNodes API key in the x-api-key header.
Params are a JSON object of named values (a positional array is rejected).

    from rpcx import RPCX
    rpcx = RPCX()                      # reads NLN_API_KEY from the environment
    out = rpcx.call("txsFor", wallets=[...], from_="2026-11-15T12:00:00Z", to="2026-11-15T13:00:00Z")
    print(out.cu, len(out.rows))
"""

from __future__ import annotations

import json
import os
import time
import urllib.request
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

ENDPOINT = "https://rpcx.mainnet.solana.nolimitnodes.com"

# JSON-RPC error codes RPCX returns (see the RPCX "Errors, limits, and billing" docs).
INVALID_PARAMS = -32602
LIMIT_EXCEEDED = -32002  # more than 10,000 rows: add `take` or narrow the filter
MINUTE_BUDGET = -32003  # the plan's CU budget for this minute is used up
NO_CU_LEFT = -32007  # the month's allowance and bought CU are both used up


@dataclass
class Result:
    rows: list[dict[str, Any]]
    cu: int
    sources: list[str] = field(default_factory=list)


class RPCXError(Exception):
    def __init__(self, code: int, message: str, data: Any = None):
        super().__init__(f"{code}: {message}")
        self.code, self.message, self.data = code, message, data


def iso(t: datetime) -> str:
    """A datetime as the RFC 3339 UTC text a `time` param takes."""
    return t.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _params(kwargs: dict[str, Any]) -> dict[str, Any]:
    # `from` is a Python keyword, so accept from_ and send it as from.
    out = {}
    for k, v in kwargs.items():
        out[k[:-1] if k.endswith("_") else k] = iso(v) if isinstance(v, datetime) else v
    return out


class RPCX:
    def __init__(self, api_key: str | None = None, endpoint: str = ENDPOINT, timeout: float = 40.0):
        self.api_key = api_key or os.environ.get("NLN_API_KEY")
        if not self.api_key:
            raise ValueError("Set NLN_API_KEY or pass api_key")
        self.endpoint, self.timeout, self._id = endpoint, timeout, 0

    def _post(self, body: Any) -> Any:
        req = urllib.request.Request(
            self.endpoint,
            data=json.dumps(body).encode(),
            headers={"Content-Type": "application/json", "x-api-key": self.api_key},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=self.timeout) as resp:
            return json.loads(resp.read())

    def _request(self, method: str, params: dict[str, Any]) -> dict[str, Any]:
        self._id += 1
        name = method if method.startswith("rpcx_") else f"rpcx_{method}"
        return {"jsonrpc": "2.0", "id": self._id, "method": name, "params": params}

    @staticmethod
    def _result(reply: dict[str, Any]) -> Result:
        if "error" in reply:
            err = reply["error"]
            raise RPCXError(err.get("code", 0), err.get("message", ""), err.get("data"))
        r = reply["result"]
        return Result(rows=r.get("rows", []), cu=r.get("cu", 0), sources=r.get("sources", []))

    def call(self, method: str, retries: int = 3, **params: Any) -> Result:
        """Call one method. Waits and retries when the per-minute CU budget (-32003) is used up."""
        for attempt in range(retries + 1):
            try:
                return self._result(self._post(self._request(method, _params(params))))
            except RPCXError as err:
                if err.code != MINUTE_BUDGET or attempt == retries:
                    raise
                time.sleep(60 - datetime.now(timezone.utc).second + 1)
        raise AssertionError("unreachable")

    def batch(self, calls: list[tuple[str, dict[str, Any]]]) -> list[Result | RPCXError]:
        """Send up to 100 calls in one request. RPCX runs them in order; each slot is a Result or an RPCXError."""
        if len(calls) > 100:
            raise ValueError("A batch holds up to 100 calls")
        requests = [self._request(m, _params(p)) for m, p in calls]
        replies = {r["id"]: r for r in self._post(requests)}
        out: list[Result | RPCXError] = []
        for req in requests:
            try:
                out.append(self._result(replies[req["id"]]))
            except RPCXError as err:
                out.append(err)
        return out
