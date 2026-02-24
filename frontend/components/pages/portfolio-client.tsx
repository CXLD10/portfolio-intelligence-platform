'use client'

import { useMemo, useState } from 'react'
import { Cell, Pie, PieChart, ResponsiveContainer, Tooltip, BarChart, Bar, XAxis, YAxis, CartesianGrid } from 'recharts'
import { AnimatedNumber } from '@/components/ui'
import { PortfolioResponse } from '@/lib/types'

const scenarios = ['Base case', '-10% shock', '-20% crash', 'Vol spike', 'Correlation spike']

export function PortfolioClient({ data }: { data: PortfolioResponse }) {
  const [scenario, setScenario] = useState('Base case')
  const [selectedAsset, setSelectedAsset] = useState<string | null>(null)

  const assets = Object.entries(data.weights).map(([name, weight]) => ({ name, weight, er: data.expected_asset_returns?.[name] ?? data.expected_return * Number(weight), risk: data.risk_contribution?.[name] ?? Number(weight) / 2 }))
  const selectedStress = data.stress_tests.find((s) => s.name.toLowerCase().includes(scenario.split(' ')[0].toLowerCase()))

  const corr = useMemo(() => {
    const names = Object.keys(data.correlation_matrix)
    return names.flatMap((r) => names.map((c) => ({ row: r, col: c, value: data.correlation_matrix[r][c] })))
  }, [data.correlation_matrix])

  return <div className='space-y-4'>
    <div className='grid md:grid-cols-4 gap-4'>
      <div className='panel'><p className='text-xs text-slate-400'>Portfolio Return</p><div className='kpi'><AnimatedNumber value={data.expected_return * 100} suffix='%' /></div></div>
      <div className='panel'><p className='text-xs text-slate-400'>Volatility</p><div className='kpi'><AnimatedNumber value={data.volatility * 100} suffix='%' /></div></div>
      <div className='panel'><p className='text-xs text-slate-400'>Scenario Drawdown</p><div className='kpi'><AnimatedNumber value={(selectedStress?.drawdown ?? -0.08) * 100} suffix='%' /></div></div>
      <div className='panel'><p className='text-xs text-slate-400'>VaR (95%)</p><div className='kpi'><AnimatedNumber value={(selectedStress?.var_95 ?? -0.12) * 100} suffix='%' /></div></div>
    </div>

    <div className='panel flex flex-wrap gap-2'>{scenarios.map((s) => <button key={s} onClick={() => setScenario(s)} className={`px-3 py-1 rounded text-sm ${scenario === s ? 'bg-slate-700' : 'bg-slate-800'}`}>{s}</button>)}</div>

    <div className='grid md:grid-cols-2 gap-4'>
      <div className='panel'><h3 className='font-semibold mb-2'>Allocation Donut</h3><div className='h-64'><ResponsiveContainer><PieChart><Pie data={assets} dataKey='weight' nameKey='name' innerRadius={50} outerRadius={90} onClick={(d: any) => setSelectedAsset(d.name)}>{assets.map((_, i) => <Cell key={i} fill={['#38bdf8','#22c55e','#f59e0b','#ef4444'][i%4]} />)}</Pie><Tooltip formatter={(v:number, _n:string,p:any)=>[`${(v*100).toFixed(2)}%`, `${p.payload.name}`]} /></PieChart></ResponsiveContainer></div>{selectedAsset && <p className='text-sm text-slate-300'>Selected: {selectedAsset}</p>}</div>
      <div className='panel'><h3 className='font-semibold mb-2'>Risk Contribution</h3><div className='h-64'><ResponsiveContainer><BarChart data={assets}><CartesianGrid stroke='#1e293b' /><XAxis dataKey='name' /><YAxis /><Tooltip /><Bar dataKey='risk' fill='#60a5fa' /></BarChart></ResponsiveContainer></div></div>
      <div className='panel md:col-span-2'><h3 className='font-semibold mb-2'>Correlation Heatmap</h3><div className='grid gap-1' style={{gridTemplateColumns:`repeat(${Object.keys(data.correlation_matrix).length},minmax(0,1fr))`}}>{corr.map((c)=><div key={`${c.row}-${c.col}`} className='p-2 text-xs rounded text-center' title={`${c.row} / ${c.col}: ${c.value.toFixed(2)}`} style={{background:`rgba(${c.value<0?239:34},${c.value<0?68:197},80,${Math.abs(c.value)})`,outline:c.row===c.col?'1px solid #e2e8f0':'none'}}>{c.value.toFixed(2)}</div>)}</div></div>
    </div>
  </div>
}
