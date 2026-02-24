import { Exchange } from '@/lib/types'

const EXCHANGES: Exchange[] = ['NSE', 'BSE', 'NASDAQ']

export function SymbolSelector({
  action,
  symbol,
  exchange,
}: {
  action: string
  symbol: string
  exchange: Exchange
}) {
  return (
    <form action={action} className='panel flex flex-wrap items-end gap-3'>
      <div>
        <label className='text-xs text-slate-400 block mb-1'>Symbol</label>
        <input
          name='symbol'
          defaultValue={symbol}
          className='bg-slate-900 border border-slate-700 rounded-md px-3 py-2 text-sm min-w-40'
          placeholder='AAPL / INFY / RELIANCE'
        />
      </div>
      <div>
        <label className='text-xs text-slate-400 block mb-1'>Exchange</label>
        <select
          name='exchange'
          defaultValue={exchange}
          className='bg-slate-900 border border-slate-700 rounded-md px-3 py-2 text-sm min-w-32'
        >
          {EXCHANGES.map((item) => (
            <option key={item} value={item}>
              {item}
            </option>
          ))}
        </select>
      </div>
      <button className='bg-slate-700 hover:bg-slate-600 rounded-md px-4 py-2 text-sm'>Analyze</button>
    </form>
  )
}
