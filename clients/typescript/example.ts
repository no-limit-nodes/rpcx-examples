/**
 * Net SOL and token flows for a list of wallets over the last hour.
 *
 *   export NLN_API_KEY=...
 *   npx tsx clients/typescript/example.ts <wallet> [<wallet> ...]
 */
import { RPCX, RPCXError, iso } from './rpcx'

const wallets = process.argv.slice(2)
if (wallets.length === 0) {
  console.error('usage: npx tsx clients/typescript/example.ts <wallet> [<wallet> ...]')
  process.exit(1)
}

const rpcx = new RPCX(process.env.NLN_API_KEY ?? '')
const to = new Date()
const from = new Date(to.getTime() - 60 * 60 * 1000)
const window = { wallets, from: iso(from), to: iso(to) }

const sol = await rpcx.call<{ address: string; txs: number; net_sol: number }>('netSol', window)
console.log(`netSol: ${sol.rows.length} wallets, ${sol.cu} CU`)
for (const row of sol.rows) console.log(`  ${row.address}  ${row.net_sol} SOL over ${row.txs} txs`)

const [flows, holdings] = await rpcx.batch([
  ['tokenFlows', window],
  ['holdings', { owners: wallets }],
])
for (const [name, r] of [['tokenFlows', flows], ['holdings', holdings]] as const) {
  if (r instanceof RPCXError) console.log(`${name}: error ${r.code} ${r.message}`)
  else console.log(`${name}: ${r.rows.length} rows, ${r.cu} CU`, r.rows.slice(0, 5))
}
