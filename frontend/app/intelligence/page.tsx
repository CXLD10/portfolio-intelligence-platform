import { Suspense } from 'react'
import dynamic from 'next/dynamic'
import { getIntelligence, getIntelligenceSummary } from '@/lib/api'
import { ErrorCard, SkeletonCard } from '@/components/ui'
import { SymbolSelector } from '@/components/symbol-selector'
import { Exchange } from '@/lib/types'

const IntelligenceClient = dynamic(() => import('@/components/pages/intelligence-client').then(m => m.IntelligenceClient), { ssr: false })

const asExchange = (value?: string): Exchange => (['NSE', 'BSE', 'NASDAQ'].includes(value || '') ? (value as Exchange) : 'NSE')

export default async function Intelligence({ searchParams }: { searchParams?: { symbol?: string; exchange?: string } }) {
  const symbol = (searchParams?.symbol || 'INFY').toUpperCase()
  const exchange = asExchange(searchParams?.exchange)

  try {
    const [d, executive] = await Promise.all([getIntelligence(symbol, exchange), getIntelligenceSummary()])
    return <div className='space-y-4'><SymbolSelector action='/intelligence' symbol={symbol} exchange={exchange} /><Suspense fallback={<SkeletonCard />}><IntelligenceClient data={d} executive={executive} /></Suspense></div>
  } catch {
    return <div className='space-y-4'><SymbolSelector action='/intelligence' symbol={symbol} exchange={exchange} /><ErrorCard title='Intelligence unavailable' message='Unable to load stock intelligence. Please retry shortly.' /></div>
  }
}
