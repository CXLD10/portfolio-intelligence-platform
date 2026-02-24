import { Suspense } from 'react'
import dynamic from 'next/dynamic'
import { getBacktest } from '@/lib/api'
import { ErrorCard, SkeletonCard } from '@/components/ui'

const BacktestClient = dynamic(() => import('@/components/pages/backtest-client').then(m => m.BacktestClient), { ssr: false })

export default async function Backtest() {
  try {
    const d = await getBacktest('AAPL', 'NASDAQ')
    return <Suspense fallback={<SkeletonCard />}><BacktestClient data={d} /></Suspense>
  } catch {
    return <ErrorCard title='Backtest unavailable' message='Unable to load strategy backtest at the moment.' />
  }
}
