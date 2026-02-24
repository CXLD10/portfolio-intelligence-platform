import { evaluatePortfolio } from '@/lib/api'
export default async function Portfolio(){const d=await evaluatePortfolio({assets:[{symbol:'AAPL',exchange:'NASDAQ',weight:0.6},{symbol:'MSFT',exchange:'NASDAQ',weight:0.4}],weighting_mode:'manual'}); return <div className='grid md:grid-cols-2 gap-4'>
<div className='panel'><h2 className='font-semibold'>Allocation</h2>{Object.entries(d.weights).map(([k,v])=><div key={k} className='text-sm flex justify-between'><span>{k}</span><span>{(Number(v)*100).toFixed(1)}%</span></div>)}</div>
<div className='panel'><h2 className='font-semibold'>Risk Metrics</h2><div className='text-sm'>Volatility: {d.volatility.toFixed(4)}</div><div className='text-sm'>Sharpe: {d.sharpe_ratio.toFixed(3)}</div></div>
<div className='panel md:col-span-2'><h2 className='font-semibold'>Stress Tests</h2>{d.stress_tests.map(s=><div key={s.name} className='text-sm flex justify-between'><span>{s.name}</span><span>{s.impact_pct.toFixed(2)}%</span></div>)}</div>
</div>}
