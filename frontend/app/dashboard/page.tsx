import { getMarketOverview } from '@/lib/api'
export default async function Dashboard(){const data=await getMarketOverview(); return <div className='grid md:grid-cols-2 gap-4'>
<div className='panel'><h2 className='font-semibold mb-2'>Sector Snapshot</h2>{Object.entries(data.sector_performance).map(([k,v])=><div key={k} className='flex justify-between text-sm'><span>{k}</span><span>{Number(v).toFixed(2)}%</span></div>)}</div>
<div className='panel'><h2 className='font-semibold mb-2'>Volatility</h2>{Object.entries(data.volatility_snapshot).map(([k,v])=><div key={k} className='flex justify-between text-sm'><span>{k}</span><span>{Number(v).toFixed(3)}</span></div>)}</div>
<div className='panel'><h2 className='font-semibold mb-2'>Top Gainers</h2>{data.top_gainers.map((g:any)=><div key={g.symbol} className='text-sm'>{g.symbol} {g.change_pct}%</div>)}</div>
<div className='panel'><h2 className='font-semibold mb-2'>Top Losers</h2>{data.top_losers.map((g:any)=><div key={g.symbol} className='text-sm'>{g.symbol} {g.change_pct}%</div>)}</div>
</div>}
