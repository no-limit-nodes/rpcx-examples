"""Call the example methods for a list of wallets over the last hour.

Save the methods first (methods/*.rpcx) in the RPCX page of the NoLimitNodes dashboard, then:

    export NLN_API_KEY=...
    python clients/python/example.py ARu4n5mFdZogZAravu7CcizaojWnS6oqka37gdLT5SZn EKmzDJWkajsqLMkY5WLWts9iUgqHCQny6hhd77fcQGN
"""

from __future__ import annotations

import sys
from datetime import datetime, timedelta, timezone

from rpcx import RPCX, RPCXError


def main(wallets: list[str]) -> None:
    rpcx = RPCX()
    to = datetime.now(timezone.utc)
    window = {"wallets": wallets, "from_": to - timedelta(hours=1), "to": to}

    activity = rpcx.call("activity", **window)
    print(f"activity: {len(activity.rows)} wallets, {activity.cu} CU")
    for row in activity.rows:
        print(f"  {row['address']}  txs={row['txs']}  failures={row['failures']}  last={row['last_tx']}")

    # Several methods in one request: up to 100 calls, run in order.
    for name, result in zip(["netSol", "tokenFlows", "solBalances"], rpcx.batch([
        ("netSol", window),
        ("tokenFlows", window),
        ("solBalances", {"wallets": wallets}),
    ])):
        if isinstance(result, RPCXError):
            print(f"{name}: error {result.code} {result.message}")
        else:
            print(f"{name}: {len(result.rows)} rows, {result.cu} CU")
            for row in result.rows[:5]:
                print(f"  {row}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise SystemExit("usage: python clients/python/example.py <wallet> [<wallet> ...]")
    main(sys.argv[1:])
