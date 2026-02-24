'use client'

import { useMemo, useState } from 'react'
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'
import { AnimatedNumber } from '@/components/ui'
import { PortfolioResponse } from '@/lib/types'

export function PortfolioClient({ data }: { data: PortfolioResponse }) {
  const [scenario, setScenario] = useState(data.stress_tests[0]?.name ?? 'baseline')
  const [selectedAsset, setSelectedAsset] = useState<string | null>(null)

  const assets = Object.entries(data.weights).map(([name, weight]) => ({
    name,
    weight,
    er: data.expected_asset_returns[name] ?? 0,
    risk: data.risk_contribution[name] ?? 0,
  }))

  const selectedStress =
    data.stress_tests.find((s) => s.name === scenario) ?? data.stress_tests[0]

  const corr = useMemo(() => {
    const names = Object.keys(data.correlation_matrix)
    return names.flatMap((r) =>
      names.map((c) => ({ row: r, col: c, value: data.correlation_matrix[r][c] })),
    )
  }, [data.correlation_matrix])

  const selectedMetrics = assets.find((a) => a.name === selectedAsset)

  return (
    <div className='space-y-4'>
      <div className='grid md:grid-cols-5 gap-4'>
        <div className='panel'>
          <p className='text-xs text-slate-400'>Expected Return</p>
          <div className='kpi'>
            <AnimatedNumber value={data.expected_return * 100} suffix='%' />
          </div>
        </div>
        <div className='panel'>
          <p className='text-xs text-slate-400'>Volatility</p>
          <div className='kpi'>
            <AnimatedNumber value={data.volatility * 100} suffix='%' />
          </div>
        </div>
        <div className='panel'>
          <p className='text-xs text-slate-400'>Sharpe Ratio</p>
          <div className='kpi'>
            <AnimatedNumber value={data.sharpe_ratio} digits={3} />
          </div>
        </div>
        <div className='panel'>
          <p className='text-xs text-slate-400'>VaR 95</p>
          <div className='kpi'>
            <AnimatedNumber value={(data.var_95 ?? -0.02) * 100} suffix='%' />
          </div>
        </div>
        <div className='panel'>
          <p className='text-xs text-slate-400'>Max Drawdown Proxy</p>
          <div className='kpi'>
            <AnimatedNumber value={(data.max_drawdown_proxy ?? -0.05) * 100} suffix='%' />
          </div>
        </div>
      </div>

      <div className='panel flex flex-wrap gap-2'>
        {data.stress_tests.map((s) => (
          <button
            key={s.name}
            onClick={() => setScenario(s.name)}
            className={`px-3 py-1 rounded text-sm ${scenario === s.name ? 'bg-slate-700' : 'bg-slate-800'}`}
          >
            {s.name}
          </button>
        ))}
      </div>

      {selectedStress && (
        <div className='grid md:grid-cols-4 gap-4'>
          <div className='panel'>
            <p className='text-xs text-slate-400'>Scenario Impact</p>
            <p className='kpi'>{selectedStress.impact_pct.toFixed(2)}%</p>
          </div>
          <div className='panel'>
            <p className='text-xs text-slate-400'>Scenario Return</p>
            <p className='kpi'>{(selectedStress.shocked_return * 100).toFixed(2)}%</p>
          </div>
          <div className='panel'>
            <p className='text-xs text-slate-400'>Scenario Volatility</p>
            <p className='kpi'>{(selectedStress.shocked_volatility * 100).toFixed(2)}%</p>
          </div>
          <div className='panel'>
            <p className='text-xs text-slate-400'>Scenario VaR 95</p>
            <p className='kpi'>{(selectedStress.shocked_var_95 * 100).toFixed(2)}%</p>
          </div>
        </div>
      )}

      <div className='grid md:grid-cols-2 gap-4'>
        <div className='panel'>
          <h3 className='font-semibold mb-2'>Allocation Donut</h3>
          <div className='h-64'>
            <ResponsiveContainer>
              <PieChart>
                <Pie
                  data={assets}
                  dataKey='weight'
                  nameKey='name'
                  innerRadius={50}
                  outerRadius={90}
                  onClick={(d: any) => setSelectedAsset(d.name)}
                >
                  {assets.map((_, i) => (
                    <Cell key={i} fill={['#38bdf8', '#22c55e', '#f59e0b', '#ef4444'][i % 4]} />
                  ))}
                </Pie>
                <Tooltip formatter={(v: number, _n: string, p: any) => [`${(v * 100).toFixed(2)}%`, p.payload.name]} />
              </PieChart>
            </ResponsiveContainer>
          </div>
          {selectedMetrics && (
            <div className='text-sm text-slate-300'>
              {selectedMetrics.name}: weight {(selectedMetrics.weight * 100).toFixed(2)}%, expected return {(selectedMetrics.er * 100).toFixed(2)}%, risk contribution {(selectedMetrics.risk * 100).toFixed(2)}%
            </div>
          )}
        </div>

        <div className='panel'>
          <h3 className='font-semibold mb-2'>Risk Contribution</h3>
          <div className='h-64'>
            <ResponsiveContainer>
              <BarChart data={assets}>
                <CartesianGrid stroke='#1e293b' />
                <XAxis dataKey='name' />
                <YAxis />
                <Tooltip formatter={(v: number) => [`${(v * 100).toFixed(2)}%`, 'Risk Contribution']} />
                <Bar dataKey='risk' fill='#60a5fa' />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className='panel md:col-span-2'>
          <h3 className='font-semibold mb-2'>Correlation Heatmap</h3>
          <div
            className='grid gap-1'
            style={{ gridTemplateColumns: `repeat(${Object.keys(data.correlation_matrix).length},minmax(0,1fr))` }}
          >
            {corr.map((c) => (
              <div
                key={`${c.row}-${c.col}`}
                className='p-2 text-xs rounded text-center'
                title={`${c.row} / ${c.col}: ${c.value.toFixed(2)}`}
                style={{
                  background: `rgba(${c.value < 0 ? 239 : 34},${c.value < 0 ? 68 : 197},80,${Math.abs(c.value)})`,
                  outline: c.row === c.col ? '1px solid #e2e8f0' : 'none',
                }}
              >
                {c.value.toFixed(2)}
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}
