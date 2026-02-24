import { Suspense } from 'react'
import dynamic from 'next/dynamic'
import { getMarketOverview } from '@/lib/api'
import { ErrorCard, SkeletonCard } from '@/components/ui'

const DashboardClient = dynamic(() => import('@/components/pages/dashboard-client').then(m => m.DashboardClient), { ssr: false })

export default async function Dashboard() {
  try {
    const data = await getMarketOverview()
    return <Suspense fallback={<SkeletonCard />}><DashboardClient data={data} /></Suspense>
  } catch {
    return <ErrorCard title='Market overview unavailable' message='Could not load market overview data from backend.' />
  }
}
