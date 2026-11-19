# RPCX Examples: Custom Solana RPC Methods for Many Wallets in One Call

Copy-paste example methods and small clients for [**RPCX**](https://nolimitnodes.com/products/rpcx) by [NoLimitNodes](https://nolimitnodes.com). RPCX lets you write your own **read-only Solana RPC methods** over the latest live chain data (transactions, instructions, logs, SOL and token balance changes, blocks, accounts and token holdings) and call them as `rpcx_<name>`. One call reads up to 1,000 wallets and returns the finished answer, instead of hundreds of raw RPC calls you join yourself.

```text
method txsFor(wallets: pubkey[] "Accounts", from: time, to: time) {
  from live_transactions
  filter (address | in wallets) && ts >= from && ts < to
  sort {-ts}
}
```

```bash
curl https://rpcx.mainnet.solana.nolimitnodes.com \
  -H "Content-Type: application/json" \
  -H "x-api-key: $NLN_API_KEY" \
  -d '{"jsonrpc":"2.0","id":1,"method":"rpcx_txsFor","params":{"wallets":["ARu4n5mFdZogZAravu7CcizaojWnS6oqka37gdLT5SZn"],"from":"2026-11-15T12:00:00Z","to":"2026-11-15T13:00:00Z"}}'
```

```json
{"jsonrpc":"2.0","id":1,"result":{"rows":[{"address":"ARu4n5mF...","sig":"2bZ38WCx...","slot":380112345,"ts":"2026-11-15 12:04:11.000","success":true,"fee":5000}],"cu":3,"sources":["lite_rpc"]}}
```

*Example output is trimmed.*

## What is RPCX?

RPCX is a NoLimitNodes service for custom Solana RPC methods. A method is a short piece of text in the RPCX method language: a header with the name and params, then a pipeline that reads live Solana data and shapes the rows. It is read-only: RPCX never sends transactions and never changes data, and it does not accept SQL. Each run is billed for the bytes it reads, in compute units (CU), and paid plans include a monthly RPCX allowance. See the [RPCX product page](https://nolimitnodes.com/products/rpcx) for plans and pricing.

## The example methods

Each file in [`methods/`](methods) is one method, ready to paste. They cover all nine live tables.

| Method | Table | Returns |
|---|---|---|
| [`txsFor`](methods/txsFor.rpcx) | `live_transactions` | Every transaction of many wallets in a window, newest first |
| [`recentFees`](methods/recentFees.rpcx) | `live_transactions` | Fees and programs of recent transactions, failed ones included |
| [`feesPaid`](methods/feesPaid.rpcx) | `live_transactions` | Fees and compute units each wallet paid as the fee payer |
| [`txsBySig`](methods/txsBySig.rpcx) | `live_transactions` | A list of transactions by signature |
| [`activity`](methods/activity.rpcx) | `live_signatures` | Transactions, failures and the latest transaction per wallet |
| [`hourlyTxs`](methods/hourlyTxs.rpcx) | `live_signatures` | Transactions per wallet and hour |
| [`programCalls`](methods/programCalls.rpcx) | `live_instructions` + `live_transactions` | Calls of one program with the fee payer and fee |
| [`topPrograms`](methods/topPrograms.rpcx) | `live_instructions` | The most called programs in a short range |
| [`logsWith`](methods/logsWith.rpcx) | `live_logs` | Log lines of an address's transactions that contain a word |
| [`netSol`](methods/netSol.rpcx) | `live_sol_balance_changes` | Net SOL change per wallet, fees included |
| [`tokenFlows`](methods/tokenFlows.rpcx) | `live_token_balance_changes` | Net token change per wallet and mint |
| [`blockStats`](methods/blockStats.rpcx) | `live_blocks` | Blocks and transactions in a slot range |
| [`solBalances`](methods/solBalances.rpcx) | `live_accounts` | The SOL balance of many wallets right now |
| [`holdersOf`](methods/holdersOf.rpcx) | `live_token_accounts` | Which of your wallets hold a token, and how much |
| [`holdings`](methods/holdings.rpcx) | `live_token_accounts` | Every non-empty token holding of many wallets |

## Quick start

1. Sign in to the [NoLimitNodes dashboard](https://dash.nolimitnodes.com/app) and open the **RPCX** page. RPCX needs an active Pro, Ultra, Max or Enterprise plan.
2. Select **New Method** and paste a file from [`methods/`](methods) into the **Code** tab. The name and params fill in.
3. Select **Validate** (free), then **Save**. The method is now callable as `rpcx_<name>`.
4. Call it with your NoLimitNodes API key, the same key as your RPC endpoint:

```bash
export NLN_API_KEY=...

# Python (standard library only)
python clients/python/example.py ARu4n5mFdZogZAravu7CcizaojWnS6oqka37gdLT5SZn

# TypeScript (Node 18+)
npm install && npx tsx clients/typescript/example.ts ARu4n5mFdZogZAravu7CcizaojWnS6oqka37gdLT5SZn

# curl
./clients/curl/examples.sh ARu4n5mFdZogZAravu7CcizaojWnS6oqka37gdLT5SZn
```

## The clients

[`clients/python/rpcx.py`](clients/python/rpcx.py) and [`clients/typescript/rpcx.ts`](clients/typescript/rpcx.ts) are small, dependency-free clients with the same shape:

```python
from rpcx import RPCX

rpcx = RPCX()  # reads NLN_API_KEY
out = rpcx.call("netSol", wallets=wallets, from_="2026-11-15T12:00:00Z", to="2026-11-15T13:00:00Z")
print(out.rows, out.cu)

results = rpcx.batch([("netSol", window), ("holdings", {"owners": wallets})])  # up to 100 calls, run in order
```

- `from` is a Python keyword, so the Python client takes `from_` and sends it as `from`. A `datetime` is sent as RFC 3339 UTC.
- When the per-minute CU budget is used up (`-32003`), `call()` waits for the next minute and retries.
- Errors raise `RPCXError` with the JSON-RPC `code`. In a batch, each failed call comes back as an `RPCXError` in its slot.

## Rules that keep methods fast and cheap

- **Give every read a key or a range right after `from`**: `(address | in wallets)`, `sig`, `program` on `live_instructions`, `owner` on `live_token_accounts`, or a `ts`/`slot` range. A range without a key may cover at most 3,000 slots.
- **Add a time range to every read by address.** Busy accounts such as programs or the USDC mint have a lot of transactions.
- **Pass many wallets in one call** with a list param (up to 1,000 values). Don't call a method once per wallet.
- **Amounts are raw integers**: lamports for SOL (divide by 1e9), base units for tokens (divide by 10^decimals).
- **Live data only**: the chain tables hold the latest Solana data, up to the newest blocks. `live_accounts` and `live_token_accounts` show current state, not history.

| Error code | Meaning | What to do |
|---|---|---|
| `-32602` | A param has the wrong type | Check the param, for example `from` must be RFC 3339 or `YYYY-MM-DD` |
| `-32002` | More than 10,000 rows | End the method with `take`, or narrow the filter |
| `-32003` | The per-minute CU budget is used up | Wait for the next minute (the clients do this) |
| `-32007` | The month's allowance and bought CU are used up | Buy CU on the RPCX page, or wait for the reset on the 1st |

Full reference: [Writing methods](https://nolimitnodes.com/docs/api-reference/rpcx/writing-methods), [Method language](https://nolimitnodes.com/docs/api-reference/rpcx/language), [Calling methods](https://nolimitnodes.com/docs/api-reference/rpcx/calling-methods) and [Errors, limits and billing](https://nolimitnodes.com/docs/api-reference/rpcx/errors-limits).

## Run the tests

The client tests mock the network and need no API key:

```bash
python -m unittest discover -s tests -v
```

## Related

- [RPCX](https://nolimitnodes.com/products/rpcx): custom read-only Solana RPC methods
- [solana-priority-fee-api](https://github.com/no-limit-nodes/solana-priority-fee-api): live priority fee estimates from NoLimitNodes RPC
- [hyperpipes-consumers](https://github.com/no-limit-nodes/hyperpipes-consumers): read decoded Solana program events from Kafka, Redis, NATS and ClickHouse

## License

[MIT](LICENSE)
