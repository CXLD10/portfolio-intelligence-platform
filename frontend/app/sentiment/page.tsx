import { Suspense } from 'react'
import dynamic from 'next/dynamic'
import { getSentiment } from '@/lib/api'
import { ErrorCard, SkeletonCard } from '@/components/ui'
import { SymbolSelector } from '@/components/symbol-selector'
import { Exchange } from '@/lib/types'

const SentimentClient = dynamic(() => import('@/components/pages/sentiment-client').then(m => m.SentimentClient), { ssr: false })

const asExchange = (value?: string): Exchange => (['NSE', 'BSE', 'NASDAQ'].includes(value || '') ? (value as Exchange) : 'NSE')

export default async function Sentiment({ searchParams }: { searchParams?: { symbol?: string; exchange?: string } }) {
  const symbol = (searchParams?.symbol || 'INFY').toUpperCase()
  const exchange = asExchange(searchParams?.exchange)

  try {
    const d = await getSentiment(symbol, exchange)
    return <div className='space-y-4'><SymbolSelector action='/sentiment' symbol={symbol} exchange={exchange} /><Suspense fallback={<SkeletonCard />}><SentimentClient data={d} /></Suspense></div>
  } catch {
    return <div className='space-y-4'><SymbolSelector action='/sentiment' symbol={symbol} exchange={exchange} /><ErrorCard title='Sentiment feed unavailable' message='Sentiment service failed to respond. Please retry shortly.' /></div>
  }
}
