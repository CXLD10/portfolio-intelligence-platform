'use client'

import { useMemo, useState } from 'react'
import { Bar, BarChart, Brush, CartesianGrid, Cell, ComposedChart, Line, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'
import { confidenceColor } from '@/components/ui'
import { IntelligenceResponse, IntelligenceSummaryResponse } from '@/lib/types'

const TIMEFRAME = { '1D': 24, '1W': 7, '1M': 30, '3M': 90, '1Y': 252 } as const

export function IntelligenceClient({ data, executive }: { data: IntelligenceResponse; executive: IntelligenceSummaryResponse | null }) {
  const [timeframe, setTimeframe] = useState<keyof typeof TIMEFRAME>('1M')
  const [showMA, setShowMA] = useState(true)
  const [showVolume, setShowVolume] = useState(true)
  const [showRSI, setShowRSI] = useState(false)
  const [execMode, setExecMode] = useState(false)

  const points = useMemo(() => {
    const raw = data.price_history?.length
      ? data.price_history
      : Array.from({ length: 252 }).map((_, i) => ({
          date: `T-${252 - i}`,
          open: 100 + Math.sin(i / 12) * 5 + i * 0.15,
          high: 102 + Math.sin(i / 12) * 5 + i * 0.15,
          low: 98 + Math.sin(i / 12) * 5 + i * 0.15,
          close: 100 + Math.sin(i / 10) * 6 + i * 0.17,
          volume: 900000 + (i % 20) * 50000,
        }))
    return raw.slice(-TIMEFRAME[timeframe]).map((p, i) => ({ ...p, ma20: data.technicals?.ma20?.[i] ?? p.close * 0.985, ma50: data.technicals?.ma50?.[i] ?? p.close * 0.96, rsi: data.technicals?.rsi?.[i] ?? 45 + Math.sin(i / 6) * 15 }))
  }, [data, timeframe])

  const features = Object.entries(data.explainability.feature_importance).sort((a, b) => Math.abs(b[1]) - Math.abs(a[1]))
  const confPct = data.confidence * 100

  return <div className='space-y-4'>
    <div className='panel flex items-center justify-between'>
      <div><p className='text-xs text-slate-400'>View Mode</p><h2 className='font-semibold'>Detailed View / Executive Summary</h2></div>
      <button onClick={() => setExecMode((v) => !v)} className='px-4 py-2 rounded-md bg-slate-800 text-sm'>{execMode ? 'Executive Summary' : 'Detailed View'}</button>
    </div>

    {execMode ? <div className='grid md:grid-cols-3 gap-4'>
      <div className='panel md:col-span-2'><h3 className='text-sm text-slate-400'>Recommendation</h3><div className='kpi mt-2'>{executive?.recommendation ?? data.recommendation}</div><p className='text-sm mt-3 text-slate-300'>{executive?.summary ?? data.summary}</p></div>
      <div className='panel'><h3 className='text-sm text-slate-400'>Confidence</h3><div className='w-full bg-slate-800 rounded-full h-4 mt-3'><div className='h-4 rounded-full transition-all' style={{ width: `${confPct}%`, background: confidenceColor(data.confidence) }} /></div><p className='mt-2 text-sm'>{confPct.toFixed(1)}%</p><p className='text-sm text-slate-400 mt-2'>Risk: {executive?.risk_level ?? data.risk_level ?? 'Medium'}</p></div>
      <div className='panel'><h3 className='font-semibold mb-2'>Top Drivers</h3>{(executive?.top_drivers ?? features.slice(0, 3).map(([k]) => k)).slice(0, 3).map((d) => <div key={d} className='text-sm text-slate-300'>{d}</div>)}</div>
      <div className='panel md:col-span-2'><h3 className='font-semibold mb-2'>Warnings</h3>{(executive?.top_warnings ?? data.warnings ?? ['Elevated sector beta', 'Macro event window']).slice(0, 2).map((w) => <div key={w} className='text-sm text-amber-300'>{w}</div>)}</div>
    </div> : <>
      <div className='panel'>
        <div className='flex flex-wrap gap-2 mb-3'>{(Object.keys(TIMEFRAME) as (keyof typeof TIMEFRAME)[]).map((t) => <button key={t} onClick={() => setTimeframe(t)} className={`px-2 py-1 rounded text-xs ${timeframe === t ? 'bg-slate-700' : 'bg-slate-800'}`}>{t}</button>)}</div>
        <div className='flex gap-4 text-xs mb-2'>
          <label><input type='checkbox' checked={showMA} onChange={(e) => setShowMA(e.target.checked)} /> MA</label>
          <label><input type='checkbox' checked={showVolume} onChange={(e) => setShowVolume(e.target.checked)} /> Volume</label>
          <label><input type='checkbox' checked={showRSI} onChange={(e) => setShowRSI(e.target.checked)} /> RSI</label>
        </div>
        <div className='h-72'>
          <ResponsiveContainer width='100%' height='100%'>
            <ComposedChart data={points}><CartesianGrid stroke='#1e293b' /><XAxis dataKey='date' hide /><YAxis yAxisId='price' /><YAxis yAxisId='volume' orientation='right' hide={!showVolume} />
              <Tooltip formatter={(v: number, n: string) => [Number(v).toFixed(2), n.toUpperCase()]} />
              <Bar dataKey='volume' yAxisId='volume' fill='#334155' hide={!showVolume} />
              <Line type='monotone' dataKey='close' yAxisId='price' stroke='#38bdf8' dot={false} />
              <Line type='monotone' dataKey='ma20' yAxisId='price' stroke='#22c55e' dot={false} hide={!showMA} />
              <Line type='monotone' dataKey='ma50' yAxisId='price' stroke='#f59e0b' dot={false} hide={!showMA} />
              <Line type='monotone' dataKey='rsi' yAxisId='price' stroke='#a78bfa' dot={false} hide={!showRSI} />
              <Brush dataKey='date' height={18} stroke='#475569' />
            </ComposedChart>
          </ResponsiveContainer>
        </div>
      </div>
      <div className='grid md:grid-cols-3 gap-4'>
        <div className='panel'><h3 className='font-semibold'>Confidence Meter</h3><div className='w-full bg-slate-800 rounded-full h-5 mt-4'><div className='h-5 rounded-full transition-all' style={{ width: `${confPct}%`, background: confidenceColor(data.confidence) }} /></div><p className='mt-2 text-sm'>{confPct.toFixed(1)}%</p></div>
        <div className='panel md:col-span-2'><h3 className='font-semibold mb-2'>Feature Importance</h3><div className='h-64'><ResponsiveContainer><BarChart data={features.map(([k, v]) => ({ feature: k, value: v, note: data.explainability.feature_notes?.[k] }))} layout='vertical'><CartesianGrid stroke='#1e293b' /><XAxis type='number' /><YAxis type='category' dataKey='feature' width={130} /><Tooltip formatter={(v: number, _: string, p: any) => [Number(v).toFixed(3), p.payload.note || 'Driver']} /><Bar dataKey='value' fill='#22c55e'>{features.map(([_, v], idx) => <Cell key={idx} fill={v < 0 ? '#ef4444' : '#22c55e'} />)}</Bar></BarChart></ResponsiveContainer></div></div>
      </div>
    </>}
  </div>
}
