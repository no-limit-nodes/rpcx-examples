<h1 align="center">Custom Solana RPC Methods: Query Many Wallets in One Call with RPCX</h1>

<p align="center">
  <b>Write your own read-only Solana RPC method, save it, and call it as <code>rpcx_&lt;name&gt;</code> for up to 1,000 wallets at once.</b><br>
  <sub>15 copy-paste RPCX methods covering all nine live tables, plus small Python, TypeScript and curl clients for <a href="https://nolimitnodes.com/products/rpcx">RPCX</a> by <a href="https://nolimitnodes.com">NoLimitNodes</a>.</sub>
</p>

<p align="center">
  <a href="./LICENSE"><img alt="MIT License" src="https://img.shields.io/badge/license-MIT-lightgrey?style=flat-square"></a>
  <a href="#the-clients"><img alt="Python | TypeScript" src="https://img.shields.io/badge/clients-Python%20%7C%20TypeScript%20%7C%20curl-blue?style=flat-square"></a>
  <a href="#the-15-example-methods"><img alt="15 methods" src="https://img.shields.io/badge/methods-15-green?style=flat-square"></a>
  <a href="#the-15-example-methods"><img alt="9 live tables" src="https://img.shields.io/badge/live%20tables-9-green?style=flat-square"></a>
  <a href="https://nolimitnodes.com"><img alt="Powered by NoLimitNodes" src="https://img.shields.io/badge/powered%20by-NoLimitNodes-FBDE00?style=flat-square&labelColor=000000"></a>
  <a href="#how-it-works"><img alt="JSON-RPC over HTTPS" src="https://img.shields.io/badge/transport-JSON--RPC%20over%20HTTPS-brightgreen?style=flat-square"></a>
  <a href="https://solana.com"><img alt="Solana Mainnet" src="https://img.shields.io/badge/solana-mainnet-9945FF?style=flat-square"></a>
</p>

<p align="center">
  <a href="#quickstart-call-your-first-rpcx-method">Quickstart</a> ·
  <a href="#the-15-example-methods">Methods</a> ·
  <a href="#the-clients">Clients</a> ·
  <a href="#rules-that-keep-methods-fast-and-cheap">Rules</a> ·
  <a href="#error-codes">Errors</a> ·
  <a href="#use-cases">Use cases</a> ·
  <a href="#faq">FAQ</a>
</p>

---

## What this is

This repo holds example **custom Solana RPC methods** for RPCX, plus the clients to call them. RPCX is a NoLimitNodes service that lets you write your own **read-only Solana RPC methods** over the latest live chain data (transactions, instructions, logs, SOL and token balance changes, blocks, accounts and token holdings) and call them as `rpcx_<name>`. One call reads up to 1,000 wallets and returns the finished answer, instead of hundreds of raw RPC calls you join yourself.

A method is a short piece of text in the RPCX method language: a header with the name and params, then a pipeline that reads live Solana data and shapes the rows. RPCX is read-only. It never sends transactions, never changes data, and does not accept SQL. Each run is billed for the bytes it reads, in compute units (CU), and paid plans include a monthly RPCX allowance. See the [RPCX product page](https://nolimitnodes.com/products/rpcx) for plans and pricing.

```text
method txsFor(wallets: pubkey[] "Accounts", from: time, to: time) {
  from live_transactions
  filter (address | in wallets) && ts >= from && ts < to
  sort {-ts}
}
```

**If you've been looking for any of these, you're in the right place:**

- A way to write **custom Solana RPC methods** and call them over JSON-RPC
- **Solana transaction history for many wallets** in one request
- A **batch Solana wallet balance** lookup (SOL balance of many wallets right now)
- **Solana token holdings for a list of wallets**, SPL Token and Token-2022
- **Net SOL change per wallet** over a time window, fees included
- **Fees paid per Solana wallet** as the fee payer, with compute units
- **Top Solana programs by instruction count** in a short range
- **Search Solana transaction logs** for a word
- A small **Python or TypeScript RPCX client** with batching and rate-limit retries

## Who this is for

- **Wallet and portfolio apps** that show balances, holdings and activity for many addresses
- **Trading and analytics teams** computing per-wallet flows, fees and transaction counts over a window
- **Bot developers** who need a fast read of a wallet list without fanning out hundreds of RPC calls
- **Backend engineers** who want the join and aggregation done server side, returning finished rows
- **Solana developers** learning the RPCX method language from working examples

## Quickstart: call your first RPCX method

### Step 1. Get an API key

Register at **[app.nolimitnodes.com/register](https://app.nolimitnodes.com/register)**. New accounts get a 5-day free Pro trial, no credit card. RPCX needs an active Pro, Ultra, Max or Enterprise plan. Your RPCX key is the same NoLimitNodes API key as your RPC endpoint.

### Step 2. Save a method

1. Open the **RPCX** page in the NoLimitNodes dashboard ([dashboard guide](https://nolimitnodes.com/docs/api-reference/rpcx/dashboard)).
2. Select **New Method** and paste a file from [`methods/`](./methods) into the **Code** tab. The name and params fill in.
3. Select **Validate** (free), then **Save**. The method is now callable as `rpcx_<name>`.

### Step 3. Clone and call it

```bash
git clone https://github.com/no-limit-nodes/rpcx-examples.git
cd rpcx-examples
export NLN_API_KEY=...

# Python (standard library only)
python clients/python/example.py ARu4n5mFdZogZAravu7CcizaojWnS6oqka37gdLT5SZn

# TypeScript (Node 18+)
npm install && npx tsx clients/typescript/example.ts ARu4n5mFdZogZAravu7CcizaojWnS6oqka37gdLT5SZn

# curl
./clients/curl/examples.sh ARu4n5mFdZogZAravu7CcizaojWnS6oqka37gdLT5SZn
```

The Python example calls `activity`, then batches `netSol`, `tokenFlows` and `solBalances`. The TypeScript example calls `netSol`, then batches `tokenFlows` and `holdings`. The curl script calls `txsFor`, then batches `netSol`, `solBalances` and `holdings`. All three use the last hour in UTC, so save those methods first. The curl script also reads `RPCX_ENDPOINT` if you need a different endpoint.

A raw call with curl looks like this:

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

## The 15 example methods

Each file in [`methods/`](./methods) is one method, ready to paste. Together they cover all nine live tables.

| Method | Params | Table | Returns |
|---|---|---|---|
| [`txsFor`](./methods/txsFor.rpcx) | `wallets`, `from`, `to` | `live_transactions` | Every transaction of many wallets in a window, newest first |
| [`recentFees`](./methods/recentFees.rpcx) | `wallets`, `from`, `to`, `limit` (100) | `live_transactions` | Fees and programs of recent transactions, failed ones included |
| [`feesPaid`](./methods/feesPaid.rpcx) | `wallets`, `from`, `to` | `live_transactions` | Fees and compute units each wallet paid as the fee payer |
| [`txsBySig`](./methods/txsBySig.rpcx) | `sigs` | `live_transactions` | A list of transactions by signature |
| [`activity`](./methods/activity.rpcx) | `wallets`, `from`, `to` | `live_signatures` | Transactions, failures and the latest transaction per wallet |
| [`hourlyTxs`](./methods/hourlyTxs.rpcx) | `wallets`, `from`, `to` | `live_signatures` | Transactions per wallet and hour |
| [`programCalls`](./methods/programCalls.rpcx) | `prog`, `from`, `to` | `live_instructions` + `live_transactions` | Calls of one program with the fee payer and fee |
| [`topPrograms`](./methods/topPrograms.rpcx) | `from`, `to`, `n` (20) | `live_instructions` | The most called programs (top-level instructions) in a short range |
| [`logsWith`](./methods/logsWith.rpcx) | `addr`, `word`, `from`, `to` | `live_logs` | Log lines of an address's transactions that contain a word |
| [`netSol`](./methods/netSol.rpcx) | `wallets`, `from`, `to` | `live_sol_balance_changes` | Net SOL change per wallet, fees included |
| [`tokenFlows`](./methods/tokenFlows.rpcx) | `wallets`, `from`, `to` | `live_token_balance_changes` | Net token change per wallet and mint, in base units |
| [`blockStats`](./methods/blockStats.rpcx) | `start`, `stop` | `live_blocks` | Blocks and transactions in a slot range (up to 3,000 slots) |
| [`solBalances`](./methods/solBalances.rpcx) | `wallets` | `live_accounts` | The SOL balance of many wallets right now |
| [`holdersOf`](./methods/holdersOf.rpcx) | `owners`, `token` | `live_token_accounts` | Which of your wallets hold a token, and how much |
| [`holdings`](./methods/holdings.rpcx) | `owners` | `live_token_accounts` | Every non-empty token holding of many wallets, SPL Token and Token-2022 |

## The clients

[`clients/python/rpcx.py`](./clients/python/rpcx.py) and [`clients/typescript/rpcx.ts`](./clients/typescript/rpcx.ts) are small, dependency-free clients with the same shape. The Python client uses only the standard library. The TypeScript client uses the built-in `fetch` (Node 18+, Deno, Bun, browsers).

```python
from rpcx import RPCX

rpcx = RPCX()  # reads NLN_API_KEY
out = rpcx.call("netSol", wallets=wallets, from_="2026-11-15T12:00:00Z", to="2026-11-15T13:00:00Z")
print(out.rows, out.cu)

results = rpcx.batch([("netSol", window), ("holdings", {"owners": wallets})])  # up to 100 calls, run in order
```

```ts
import { RPCX, iso } from './rpcx'

const rpcx = new RPCX(process.env.NLN_API_KEY!)
const { rows, cu } = await rpcx.call('txsFor', { wallets, from: '2026-11-15T12:00:00Z', to: '2026-11-15T13:00:00Z' })
```

- Every call returns `rows`, `cu` and `sources`. A method name without the `rpcx_` prefix gets it added.
- Params are a JSON object of named values. A positional array is rejected.
- `from` is a Python keyword, so the Python client takes `from_` and sends it as `from`. A `datetime` is sent as RFC 3339 UTC. In TypeScript, `iso(date)` does the same.
- When the per-minute CU budget is used up (`-32003`), `call()` waits for the next minute and retries (3 retries by default).
- Errors raise `RPCXError` with the JSON-RPC `code`. In a batch, each failed call comes back as an `RPCXError` in its slot.
- A batch holds up to 100 calls. RPCX runs them in order.

## Rules that keep methods fast and cheap

- **Give every read a key or a range right after `from`**: `(address | in wallets)`, `sig`, `program` on `live_instructions`, `owner` on `live_token_accounts`, or a `ts`/`slot` range. A range without a key may cover at most 3,000 slots.
- **Add a time range to every read by address.** Busy accounts such as programs or the USDC mint have a lot of transactions.
- **Pass many wallets in one call** with a list param (up to 1,000 values). Don't call a method once per wallet.
- **Amounts are raw integers**: lamports for SOL (divide by 1e9), base units for tokens (divide by 10^decimals).
- **Live data only**: the chain tables hold the latest Solana data, up to the newest blocks. `live_accounts` and `live_token_accounts` show current state, not history.

## Error codes

| Error code | Meaning | What to do |
|---|---|---|
| `-32602` | A param has the wrong type | Check the param, for example `from` must be RFC 3339 or `YYYY-MM-DD` |
| `-32002` | More than 10,000 rows | End the method with `take`, or narrow the filter |
| `-32003` | The per-minute CU budget is used up | Wait for the next minute (the clients do this) |
| `-32007` | The month's allowance and bought CU are used up | Buy CU on the RPCX page, or wait for the reset on the 1st |

Full reference: [Writing methods](https://nolimitnodes.com/docs/api-reference/rpcx/writing-methods), [Method language](https://nolimitnodes.com/docs/api-reference/rpcx/language), [Calling methods](https://nolimitnodes.com/docs/api-reference/rpcx/calling-methods) and [Errors, limits and billing](https://nolimitnodes.com/docs/api-reference/rpcx/errors-limits).

## Run the tests

The client tests mock the network and need no API key. They also check that every file in `methods/` has a matching method header.

```bash
python -m unittest discover -s tests -v
```

Type-check the TypeScript client with `npm run typecheck`.

## Use cases

### Wallet and portfolio views

- **Balances for a wallet list.** `solBalances` returns the SOL balance of many wallets right now. An address with no account returns no row.
- **Token holdings.** `holdings` lists every non-empty holding of many wallets. `holdersOf` answers which of your wallets hold one mint, and how much.
- **Activity summaries.** `activity` returns transactions, failures and the latest transaction per wallet. `hourlyTxs` buckets them by hour.

### Flows and fees

- **Net SOL and token flows.** `netSol` and `tokenFlows` aggregate balance changes per wallet (and per mint) over a window.
- **Fee accounting.** `feesPaid` sums fees and compute units each wallet paid as the fee payer. `recentFees` lists fees and programs of recent transactions, failed ones included.

### Programs, logs and blocks

- **Program usage.** `topPrograms` ranks programs by top-level instruction count. `programCalls` lists one program's instructions joined to the fee payer and fee.
- **Log search.** `logsWith` finds log lines of an address's transactions that contain a word.
- **Slot stats.** `blockStats` counts blocks and transactions in a slot range.

## How it works

You save a method in the RPCX dashboard. RPCX exposes it as the JSON-RPC method `rpcx_<name>` at `https://rpcx.mainnet.solana.nolimitnodes.com`. You POST a JSON-RPC 2.0 request with your NoLimitNodes API key in the `x-api-key` header and named params. RPCX runs the pipeline over the live tables and returns `rows`, the `cu` the run cost, and the `sources` it read. Send an array of requests for a batch.

## RPCX vs standard Solana RPC: when to pick which

**Pick RPCX** when the answer needs many wallets, a time window, or a join and aggregation. One `rpcx_` call reads up to 1,000 wallets and returns the finished rows, instead of hundreds of raw RPC calls you join yourself.

**Stay on standard Solana RPC** when you need to send transactions or read history older than the live tables. RPCX is read-only and covers the latest live chain data. `live_accounts` and `live_token_accounts` show current state, not history.

## Repo layout

```
.
├── methods/                  # 15 RPCX methods, one per file, ready to paste
│   ├── activity.rpcx
│   ├── blockStats.rpcx
│   ├── feesPaid.rpcx
│   ├── holdersOf.rpcx
│   ├── holdings.rpcx
│   ├── hourlyTxs.rpcx
│   ├── logsWith.rpcx
│   ├── netSol.rpcx
│   ├── programCalls.rpcx
│   ├── recentFees.rpcx
│   ├── solBalances.rpcx
│   ├── tokenFlows.rpcx
│   ├── topPrograms.rpcx
│   ├── txsBySig.rpcx
│   └── txsFor.rpcx
├── clients/
│   ├── python/
│   │   ├── rpcx.py           # standard-library client
│   │   └── example.py
│   ├── typescript/
│   │   ├── rpcx.ts           # fetch-based client
│   │   └── example.ts
│   └── curl/
│       └── examples.sh
├── tests/
│   └── test_python_client.py # mocked network, no API key needed
├── package.json
├── tsconfig.json
├── LICENSE                   # MIT
└── README.md
```

## FAQ

<details>
<summary><b>What is RPCX on Solana?</b></summary>

RPCX is a NoLimitNodes service for custom, read-only Solana RPC methods. You write a short method in the RPCX method language, save it in the dashboard, and call it as `rpcx_<name>` over JSON-RPC. It reads live transactions, instructions, logs, balance changes, blocks, accounts and token holdings, and returns finished rows.
</details>

<details>
<summary><b>How do I get the transaction history of many Solana wallets in one call?</b></summary>

Save [`txsFor`](./methods/txsFor.rpcx) and call `rpcx_txsFor` with a `wallets` list and a `from`/`to` window. A list param takes up to 1,000 values, so one request covers the whole set. Results come back newest first. Keep the window tight for busy accounts, and add `take` if you could pass 10,000 rows.
</details>

<details>
<summary><b>How do I check the SOL balance of many wallets at once?</b></summary>

Use [`solBalances`](./methods/solBalances.rpcx). It reads `live_accounts` for every wallet in the list and returns the SOL balance, owner and slot, sorted by balance. An address with no account returns no row. It shows current state only. For changes over a window, use [`netSol`](./methods/netSol.rpcx) instead.
</details>

<details>
<summary><b>Can RPCX send transactions or run SQL?</b></summary>

No. RPCX is read-only. It never sends transactions, never changes data, and does not accept SQL. Methods are written in the RPCX method language: a header with the name and params, then a pipeline of steps such as `from`, `filter`, `group`, `aggregate`, `sort` and `take` over the live tables.
</details>

<details>
<summary><b>How is RPCX billed?</b></summary>

Each run is billed for the bytes it reads, in compute units (CU). Every response includes the `cu` it cost. Paid plans include a monthly RPCX allowance and a per-minute CU budget. When the minute budget runs out you get `-32003`. When the month's allowance and bought CU run out you get `-32007`. See the product page for pricing.
</details>

<details>
<summary><b>Why does my RPCX method return error -32002?</b></summary>

The method would return more than 10,000 rows. End it with `take`, as `recentFees` and `topPrograms` do, or narrow the filter with a shorter time range or fewer wallets. A read with a range but no key may also cover at most 3,000 slots, so give every read a key or a tight range.
</details>

<details>
<summary><b>Do I need a different API key for RPCX?</b></summary>

No. RPCX uses the same NoLimitNodes API key as your RPC endpoint, sent in the `x-api-key` header. The Python client reads it from `NLN_API_KEY`. The TypeScript client takes it as a constructor argument. RPCX needs an active Pro, Ultra, Max or Enterprise plan.
</details>

## Learn more on NoLimitNodes Academy

- [What is a Solana RPC node?](https://nolimitnodes.com/academy/what-is-a-solana-rpc-node). Background on the standard RPC that RPCX methods sit beside.
- [Solana slots, blocks and commitment explained](https://nolimitnodes.com/academy/solana-slots-blocks-commitment-explained). Useful when you write `slot` and `ts` ranges such as `blockStats`.
- [Solana snippets](https://nolimitnodes.com/academy/snippets). Short copy-paste code to pair with these methods.
- [NoLimitNodes Academy](https://nolimitnodes.com/academy). The full set of guides, walkthroughs and workbooks.

## Contributing

Issues and pull requests are welcome. If you add a method, put it in `methods/` as `<name>.rpcx` with a one-line comment on top, and run the tests: they check that the file name matches the method header.

## License

[MIT](./LICENSE).

## Related resources

- [RPCX](https://nolimitnodes.com/products/rpcx): custom read-only Solana RPC methods
- [RPCX overview](https://nolimitnodes.com/docs/api-reference/rpcx/overview) and [RPCX quickstart](https://nolimitnodes.com/docs/quickstarts/rpcx)
- [RPCX tables](https://nolimitnodes.com/docs/api-reference/rpcx/tables), [popular tables](https://nolimitnodes.com/docs/api-reference/rpcx/popular-tables) and [all tables](https://nolimitnodes.com/docs/api-reference/rpcx/all-tables)
- [RPCX MCP docs](https://nolimitnodes.com/docs/api-reference/rpcx/mcp)
- [NoLimitNodes Solana RPC nodes](https://nolimitnodes.com/products/rpc-nodes) and [documentation](https://nolimitnodes.com/docs/)
- [solana-priority-fee-api](https://github.com/no-limit-nodes/solana-priority-fee-api): live priority fee estimates from NoLimitNodes RPC
- [hyperpipes-consumers](https://github.com/no-limit-nodes/hyperpipes-consumers): read decoded Solana program events from Kafka, Redis, NATS and ClickHouse
- [JSON-RPC 2.0 specification](https://www.jsonrpc.org/specification)
- [Solana RPC documentation](https://solana.com/docs/rpc)

---

<p align="center">
  <b>Ready to replace hundreds of RPC calls with one?</b><br>
  <a href="https://app.nolimitnodes.com/register">Register, get a 5-day free Pro trial, grab your API key →</a>
</p>
