/**
 * A small TypeScript client for NoLimitNodes RPCX methods. Uses the built-in fetch (Node 18+, Deno, Bun, browsers).
 *
 * A saved RPCX method is a JSON-RPC method called rpcx_<name> at https://rpcx.mainnet.solana.nolimitnodes.com,
 * with your NoLimitNodes API key in the x-api-key header. Params are an object of named values.
 *
 *   const rpcx = new RPCX(process.env.NLN_API_KEY!)
 *   const { rows, cu } = await rpcx.call('txsFor', { wallets, from: '2026-11-15T12:00:00Z', to: '2026-11-15T13:00:00Z' })
 */

export const ENDPOINT = 'https://rpcx.mainnet.solana.nolimitnodes.com'

export const ErrorCode = {
  InvalidParams: -32602,
  LimitExceeded: -32002, // more than 10,000 rows: add `take` or narrow the filter
  MinuteBudget: -32003, // the plan's CU budget for this minute is used up
  NoCuLeft: -32007, // the month's allowance and bought CU are both used up
} as const

export type Params = Record<string, string | number | boolean | null | Array<string | number>>

export interface Result<Row = Record<string, unknown>> {
  rows: Row[]
  cu: number
  sources: string[]
}

export class RPCXError extends Error {
  constructor(public code: number, message: string, public data?: unknown) {
    super(`${code}: ${message}`)
  }
}

interface Reply<Row> {
  id: number
  result?: Result<Row>
  error?: { code: number; message: string; data?: unknown }
}

export class RPCX {
  private id = 0

  constructor(private apiKey: string, private endpoint: string = ENDPOINT) {
    if (!apiKey) throw new Error('Pass your NoLimitNodes API key')
  }

  private request(method: string, params: Params) {
    return { jsonrpc: '2.0', id: ++this.id, method: method.startsWith('rpcx_') ? method : `rpcx_${method}`, params }
  }

  private async post<T>(body: unknown): Promise<T> {
    const res = await fetch(this.endpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'x-api-key': this.apiKey },
      body: JSON.stringify(body),
    })
    if (!res.ok) throw new Error(`HTTP ${res.status}`)
    return (await res.json()) as T
  }

  private static unwrap<Row>(reply: Reply<Row>): Result<Row> {
    if (reply.error) throw new RPCXError(reply.error.code, reply.error.message, reply.error.data)
    const r = reply.result!
    return { rows: r.rows ?? [], cu: r.cu ?? 0, sources: r.sources ?? [] }
  }

  /** Call one method. Waits for the next minute and retries when the per-minute CU budget is used up. */
  async call<Row = Record<string, unknown>>(method: string, params: Params = {}, retries = 3): Promise<Result<Row>> {
    for (let attempt = 0; ; attempt++) {
      try {
        return RPCX.unwrap(await this.post<Reply<Row>>(this.request(method, params)))
      } catch (err) {
        if (!(err instanceof RPCXError) || err.code !== ErrorCode.MinuteBudget || attempt >= retries) throw err
        await new Promise(r => setTimeout(r, (61 - new Date().getUTCSeconds()) * 1000))
      }
    }
  }

  /** Up to 100 calls in one request, run in order. Each slot is a Result or an RPCXError. */
  async batch(calls: Array<[method: string, params: Params]>): Promise<Array<Result | RPCXError>> {
    if (calls.length > 100) throw new Error('A batch holds up to 100 calls')
    const requests = calls.map(([m, p]) => this.request(m, p))
    const replies = new Map((await this.post<Reply<Record<string, unknown>>[]>(requests)).map(r => [r.id, r]))
    return requests.map(req => {
      try {
        return RPCX.unwrap(replies.get(req.id)!)
      } catch (err) {
        return err as RPCXError
      }
    })
  }
}

/** A Date as the RFC 3339 UTC text a `time` param takes. */
export const iso = (d: Date) => d.toISOString().replace(/\.\d{3}Z$/, 'Z')
