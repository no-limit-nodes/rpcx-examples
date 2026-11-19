#!/usr/bin/env bash
# Call RPCX methods with curl. Save the methods in methods/ first, then:
#   export NLN_API_KEY=...
#   ./clients/curl/examples.sh ARu4n5mFdZogZAravu7CcizaojWnS6oqka37gdLT5SZn
set -euo pipefail

: "${NLN_API_KEY:?Set NLN_API_KEY to your NoLimitNodes API key}"
ENDPOINT="${RPCX_ENDPOINT:-https://rpcx.mainnet.solana.nolimitnodes.com}"
WALLET="${1:-ARu4n5mFdZogZAravu7CcizaojWnS6oqka37gdLT5SZn}"

# The last hour, in UTC (works with GNU and BSD date).
TO=$(date -u +%Y-%m-%dT%H:%M:%SZ)
FROM=$(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%SZ 2>/dev/null || date -u -v-1H +%Y-%m-%dT%H:%M:%SZ)

rpcx() {
  curl -sS "$ENDPOINT" -H "Content-Type: application/json" -H "x-api-key: $NLN_API_KEY" -d "$1"
  echo
}

echo "# One call: every transaction of a wallet in the last hour"
rpcx "{\"jsonrpc\":\"2.0\",\"id\":1,\"method\":\"rpcx_txsFor\",\"params\":{\"wallets\":[\"$WALLET\"],\"from\":\"$FROM\",\"to\":\"$TO\"}}"

echo "# A batch: up to 100 calls in one request, run in order"
rpcx "[
  {\"jsonrpc\":\"2.0\",\"id\":1,\"method\":\"rpcx_netSol\",\"params\":{\"wallets\":[\"$WALLET\"],\"from\":\"$FROM\",\"to\":\"$TO\"}},
  {\"jsonrpc\":\"2.0\",\"id\":2,\"method\":\"rpcx_solBalances\",\"params\":{\"wallets\":[\"$WALLET\"]}},
  {\"jsonrpc\":\"2.0\",\"id\":3,\"method\":\"rpcx_holdings\",\"params\":{\"owners\":[\"$WALLET\"]}}
]"
