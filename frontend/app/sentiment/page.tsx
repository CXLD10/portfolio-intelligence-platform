import { Suspense } from 'react'
import dynamic from 'next/dynamic'
import { getSentiment } from '@/lib/api'
import { ErrorCard, SkeletonCard } from '@/components/ui'

const SentimentClient = dynamic(() => import('@/components/pages/sentiment-client').then(m => m.SentimentClient), { ssr: false })

export default async function Sentiment() {
  try {
    const d = await getSentiment('INFY', 'NSE')
    return <Suspense fallback={<SkeletonCard />}><SentimentClient data={d} /></Suspense>
  } catch {
    return <ErrorCard title='Sentiment feed unavailable' message='Sentiment service failed to respond. Please retry shortly.' />
  }
}
