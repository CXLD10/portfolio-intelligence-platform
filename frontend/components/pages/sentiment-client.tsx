'use client'

import { Bar, CartesianGrid, ComposedChart, Line, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'
import { momentumLabel } from '@/components/ui'

export function SentimentClient({ data }: { data: any }) {
  const trend = data.sentiment_trend?.length ? data.sentiment_trend.map((s: number, i: number) => ({ t: i, sentiment: s, price: 100 + i * 0.5 + Math.sin(i / 3) * 2 })) : Array.from({ length: 30 }).map((_, i) => ({ t: i, sentiment: 0.45 + Math.sin(i / 4) * 0.2, price: 100 + i * 0.4 + Math.sin(i / 5) * 3 }))
  const momentum = trend[trend.length - 1].sentiment - trend[Math.max(trend.length - 5, 0)].sentiment
  const dist = [{ side: 'Bull', value: data.bullish_ratio ?? 0.56 }, { side: 'Bear', value: data.bearish_ratio ?? 0.31 }, { side: 'Neutral', value: 1 - (data.bullish_ratio ?? 0.56) - (data.bearish_ratio ?? 0.31) }]

  return <div className='space-y-4'>
    <div className='grid md:grid-cols-3 gap-4'>
      <div className='panel'><p className='text-xs text-slate-400'>Sentiment Score</p><p className='kpi'>{(data.sentiment_score ?? 0.61).toFixed(2)}</p></div>
      <div className='panel'><p className='text-xs text-slate-400'>Divergence vs Price</p><p className='kpi'>{(data.divergence_vs_price ?? 0.08).toFixed(2)}</p></div>
      <div className='panel'><p className='text-xs text-slate-400'>Momentum</p><p className='kpi text-xl'>{momentumLabel(momentum)}</p></div>
    </div>
    <div className='panel'><h3 className='font-semibold'>Sentiment vs Price Trend</h3><div className='h-72'><ResponsiveContainer><ComposedChart data={trend}><CartesianGrid stroke='#1e293b' /><XAxis dataKey='t' /><YAxis yAxisId='s' /><YAxis yAxisId='p' orientation='right' /><Tooltip /><Line yAxisId='s' dataKey='sentiment' stroke='#38bdf8' dot={false} /><Line yAxisId='p' dataKey='price' stroke='#22c55e' dot={false} /></ComposedChart></ResponsiveContainer></div></div>
    <div className='panel'><h3 className='font-semibold'>Bull / Bear Distribution</h3><div className='h-52'><ResponsiveContainer><ComposedChart data={[{ name: 'Distribution', ...Object.fromEntries(dist.map(d => [d.side, d.value])) }]}><CartesianGrid stroke='#1e293b' /><XAxis dataKey='name' /><YAxis /><Tooltip /><Bar dataKey='Bull' stackId='a' fill='#22c55e' /><Bar dataKey='Neutral' stackId='a' fill='#64748b' /><Bar dataKey='Bear' stackId='a' fill='#ef4444' /></ComposedChart></ResponsiveContainer></div></div>
  </div>
}
