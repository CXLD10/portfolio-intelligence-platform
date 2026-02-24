import { Suspense } from 'react'
import dynamic from 'next/dynamic'
import { getIntelligence, getIntelligenceSummary } from '@/lib/api'
import { ErrorCard, SkeletonCard } from '@/components/ui'

const IntelligenceClient = dynamic(() => import('@/components/pages/intelligence-client').then(m => m.IntelligenceClient), { ssr: false })

export default async function Intelligence() {
  try {
    const [d, executive] = await Promise.all([getIntelligence('INFY', 'NSE'), getIntelligenceSummary()])
    return <Suspense fallback={<SkeletonCard />}><IntelligenceClient data={d} executive={executive} /></Suspense>
  } catch {
    return <ErrorCard title='Intelligence unavailable' message='Unable to load stock intelligence. Please retry shortly.' />
  }
}
