'use client'

import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'

export function DashboardClient({ data }: { data: any }) {
  const sectors = Object.entries(data.sector_performance || {}).map(([name, perf]) => ({ name, perf: Number(perf), vol: Number(data.volatility_snapshot?.[name] ?? 0.2) }))
  const cap = [{ bucket: 'Large', v: 0.52 }, { bucket: 'Mid', v: 0.31 }, { bucket: 'Small', v: 0.17 }]
  const exch = [{ name: 'NSE', open: true }, { name: 'BSE', open: false }, { name: 'NASDAQ', open: true }]

  return <div className='space-y-4'>
    <div className='grid md:grid-cols-4 gap-4'>
      <div className='panel md:col-span-2'><p className='text-xs text-slate-400'>Primary KPI</p><p className='kpi'>Breadth {((data.market_breadth ?? 0.61) * 100).toFixed(1)}%</p></div>
      <div className='panel'><p className='text-xs text-slate-400'>Top Gainer</p><p className='kpi text-xl'>{data.top_gainers?.[0]?.symbol ?? 'N/A'}</p></div>
      <div className='panel'><p className='text-xs text-slate-400'>Top Loser</p><p className='kpi text-xl'>{data.top_losers?.[0]?.symbol ?? 'N/A'}</p></div>
    </div>
    <div className='grid md:grid-cols-2 gap-4'>
      <div className='panel'><h3 className='font-semibold mb-2'>Sector Heatmap</h3><div className='grid grid-cols-3 gap-2'>{sectors.map(s=><div key={s.name} title={`Volatility: ${s.vol.toFixed(2)}`} className='rounded p-3 text-sm' style={{background:s.perf>=0?'rgba(34,197,94,.18)':'rgba(239,68,68,.2)'}}><div>{s.name}</div><div className='text-xs'>{s.perf.toFixed(2)}%</div></div>)}</div></div>
      <div className='panel'><h3 className='font-semibold mb-2'>Market Cap Distribution</h3><div className='h-64'><ResponsiveContainer><BarChart data={cap}><CartesianGrid stroke='#1e293b' /><XAxis dataKey='bucket' /><YAxis /><Tooltip /><Bar dataKey='v' fill='#60a5fa' /></BarChart></ResponsiveContainer></div></div>
      <div className='panel md:col-span-2'><h3 className='font-semibold mb-2'>Exchange Status</h3><div className='flex gap-2'>{exch.map(e=><span key={e.name} className={`px-3 py-1 rounded-full text-xs ${e.open?'bg-green-900/60 text-green-200':'bg-slate-800 text-slate-300'}`}>{e.name}: {e.open?'OPEN':'CLOSED'}</span>)}</div></div>
    </div>
  </div>
}
