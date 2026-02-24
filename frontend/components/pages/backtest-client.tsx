'use client'

import { useMemo, useState } from 'react'
import { ColumnDef, flexRender, getCoreRowModel, getExpandedRowModel, getFilteredRowModel, getSortedRowModel, useReactTable } from '@tanstack/react-table'
import { Area, AreaChart, CartesianGrid, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'

export function BacktestClient({ data }: { data: any }) {
  const [filter, setFilter] = useState('')
  const curve = useMemo(() => (data.equity_curve?.length ? data.equity_curve : Array.from({ length: 180 }).map((_, i) => ({ t: i, strategy: 100 + i * 0.2 + Math.sin(i / 8) * 4, benchmark: 100 + i * 0.15, drawdown: -Math.abs(Math.sin(i / 11) * 0.12) }))), [data])
  const trades = data.trade_log?.length ? data.trade_log : Array.from({ length: 24 }).map((_, i) => ({ index: i + 1, signal: i % 2 ? 'BUY' : 'SELL', pnl: (Math.sin(i) * 2).toFixed(2), details: `Trade ${i + 1} rationale and slippage` }))

  const columns = useMemo<ColumnDef<any>[]>(() => [
    { accessorKey: 'index', header: 'ID' },
    { accessorKey: 'signal', header: 'Signal' },
    { accessorKey: 'pnl', header: 'PnL' },
  ], [])

  const table = useReactTable({ data: trades, columns, state: { globalFilter: filter }, onGlobalFilterChange: setFilter, getCoreRowModel: getCoreRowModel(), getSortedRowModel: getSortedRowModel(), getFilteredRowModel: getFilteredRowModel(), getExpandedRowModel: getExpandedRowModel() })

  return <div className='space-y-4'>
    <div className='grid md:grid-cols-5 gap-4'>
      <div className='panel'><p className='text-xs text-slate-400'>Strategy Return</p><p className='kpi'>{(data.strategy_return*100).toFixed(2)}%</p></div>
      <div className='panel'><p className='text-xs text-slate-400'>Benchmark Return</p><p className='kpi'>{(data.buy_hold_return*100).toFixed(2)}%</p></div>
      <div className='panel'><p className='text-xs text-slate-400'>Active Return</p><p className='kpi'>{((data.strategy_return-data.buy_hold_return)*100).toFixed(2)}%</p></div>
      <div className='panel'><p className='text-xs text-slate-400'>Information Ratio</p><p className='kpi'>{(data.information_ratio ?? 0.78).toFixed(2)}</p></div>
      <div className='panel'><p className='text-xs text-slate-400'>Max DD</p><p className='kpi'>{(data.max_drawdown*100).toFixed(2)}%</p></div>
    </div>
    <div className='panel'><h3 className='font-semibold'>Equity Curve vs Benchmark</h3><div className='h-72'><ResponsiveContainer><LineChart data={curve}><CartesianGrid stroke='#1e293b' /><XAxis dataKey='t' /><YAxis /><Tooltip formatter={(v:number,n:string,p:any)=>[Number(v).toFixed(2),`${n} | DD ${(p.payload.drawdown*100).toFixed(2)}%`]} /><Line type='monotone' dataKey='strategy' stroke='#22c55e' dot={false} /><Line type='monotone' dataKey='benchmark' stroke='#94a3b8' dot={false} /></LineChart></ResponsiveContainer></div></div>
    <div className='panel'><h3 className='font-semibold'>Drawdown</h3><div className='h-44'><ResponsiveContainer><AreaChart data={curve}><CartesianGrid stroke='#1e293b' /><XAxis dataKey='t' /><YAxis /><Tooltip /><Area dataKey='drawdown' fill='#ef4444' stroke='#ef4444' /></AreaChart></ResponsiveContainer></div></div>
    <div className='panel'><div className='flex items-center justify-between mb-2'><h3 className='font-semibold'>Trade Log</h3><input className='bg-slate-900 border border-slate-700 rounded px-2 py-1 text-sm' placeholder='Filter trades' value={filter} onChange={e=>setFilter(e.target.value)} /></div><table className='w-full text-sm'><thead>{table.getHeaderGroups().map(hg=><tr key={hg.id}>{hg.headers.map(h=><th key={h.id} className='text-left py-1 cursor-pointer' onClick={h.column.getToggleSortingHandler()}>{flexRender(h.column.columnDef.header,h.getContext())}</th>)}</tr>)}</thead><tbody>{table.getRowModel().rows.map(r=>[<tr key={r.id} className='border-t border-slate-800' onClick={r.getToggleExpandedHandler()}>{r.getVisibleCells().map(c=><td key={c.id} className='py-1'>{flexRender(c.column.columnDef.cell,c.getContext())}</td>)}</tr>, r.getIsExpanded() ? <tr key={`${r.id}-details`}><td colSpan={3} className='text-xs text-slate-400 py-2'>Details: {r.original.details ?? JSON.stringify(r.original)}</td></tr> : null])}</tbody></table></div>
  </div>
}
