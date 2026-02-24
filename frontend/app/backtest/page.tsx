import { getBacktest } from '@/lib/api'
export default async function Backtest(){const d=await getBacktest('AAPL','NASDAQ'); return <div className='grid md:grid-cols-2 gap-4'>
<div className='panel'><h2 className='font-semibold'>Performance</h2><div className='text-sm'>Strategy: {(d.strategy_return*100).toFixed(2)}%</div><div className='text-sm'>Buy/Hold: {(d.buy_hold_return*100).toFixed(2)}%</div></div>
<div className='panel'><h2 className='font-semibold'>Risk</h2><div className='text-sm'>Max DD: {(d.max_drawdown*100).toFixed(2)}%</div><div className='text-sm'>Win rate: {(d.win_rate*100).toFixed(2)}%</div></div>
<div className='panel md:col-span-2'><h2 className='font-semibold'>Trade Log</h2>{d.trade_log.slice(0,10).map((t:any)=><div key={t.index} className='text-xs'>{t.index} | {t.signal} | {t.strategy_return}</div>)}</div>
</div>}
