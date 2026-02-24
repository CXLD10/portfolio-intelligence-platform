import { getSentiment } from '@/lib/api'
export default async function Sentiment(){const d=await getSentiment('INFY','NSE'); return <div className='grid md:grid-cols-3 gap-4'>
<div className='panel'><h2 className='font-semibold'>Score</h2><div>{d.sentiment_score.toFixed(3)}</div></div>
<div className='panel'><h2 className='font-semibold'>Bull / Bear</h2><div>{(d.bullish_ratio*100).toFixed(1)}% / {(d.bearish_ratio*100).toFixed(1)}%</div></div>
<div className='panel'><h2 className='font-semibold'>Divergence</h2><div>{d.divergence_vs_price.toFixed(3)}</div></div>
<div className='panel md:col-span-3'><h2 className='font-semibold'>Trend</h2><div className='text-sm'>{d.sentiment_trend.join(' | ')}</div></div>
</div>}
