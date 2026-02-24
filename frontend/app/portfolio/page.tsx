import { Suspense } from 'react'
import dynamic from 'next/dynamic'
import { evaluatePortfolio } from '@/lib/api'
import { ErrorCard, SkeletonCard } from '@/components/ui'

const PortfolioClient = dynamic(() => import('@/components/pages/portfolio-client').then(m => m.PortfolioClient), { ssr: false })

export default async function Portfolio() {
  try {
    const d = await evaluatePortfolio({ assets: [{ symbol: 'AAPL', exchange: 'NASDAQ', weight: 0.6 }, { symbol: 'MSFT', exchange: 'NASDAQ', weight: 0.4 }], weighting_mode: 'manual' })
    return <Suspense fallback={<SkeletonCard />}><PortfolioClient data={d} /></Suspense>
  } catch {
    return <ErrorCard title='Portfolio module unavailable' message='Could not evaluate portfolio. Verify backend connectivity and retry.' />
  }
}
