import { Suspense } from 'react'
import dynamic from 'next/dynamic'
import { getBacktest } from '@/lib/api'
import { ErrorCard, SkeletonCard } from '@/components/ui'
import { SymbolSelector } from '@/components/symbol-selector'
import { Exchange } from '@/lib/types'

const BacktestClient = dynamic(() => import('@/components/pages/backtest-client').then(m => m.BacktestClient), { ssr: false })

const asExchange = (value?: string): Exchange => (['NSE', 'BSE', 'NASDAQ'].includes(value || '') ? (value as Exchange) : 'NASDAQ')

export default async function Backtest({ searchParams }: { searchParams?: { symbol?: string; exchange?: string } }) {
  const symbol = (searchParams?.symbol || 'AAPL').toUpperCase()
  const exchange = asExchange(searchParams?.exchange)

  try {
    const d = await getBacktest(symbol, exchange)
    return <div className='space-y-4'><SymbolSelector action='/backtest' symbol={symbol} exchange={exchange} /><Suspense fallback={<SkeletonCard />}><BacktestClient data={d} /></Suspense></div>
  } catch {
    return <div className='space-y-4'><SymbolSelector action='/backtest' symbol={symbol} exchange={exchange} /><ErrorCard title='Backtest unavailable' message='Unable to load strategy backtest at the moment.' /></div>
  }
}
