import { cache } from 'react'
import {
  IntelligenceResponse,
  IntelligenceSummaryResponse,
  PortfolioResponse,
  BacktestResponse,
} from './types'

const API = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

async function fetchJson<T>(path: string, init?: RequestInit): Promise<T> {
  const r = await fetch(`${API}${path}`, { cache: 'no-store', ...init })
  if (!r.ok) throw new Error(`Request failed: ${path}`)
  return r.json() as Promise<T>
}

export const getIntelligence = cache(async (symbol: string, exchange: string) =>
  fetchJson<IntelligenceResponse>(`/api/v1/intelligence?symbol=${symbol}&exchange=${exchange}`),
)

export const getIntelligenceSummary = cache(async () => {
  try {
    return await fetchJson<IntelligenceSummaryResponse>(`/api/v1/intelligence/summary`)
  } catch {
    return null
  }
})

export const getMarketOverview = cache(async () => fetchJson<any>(`/api/v1/market/overview`))

export const getSentiment = cache(async (symbol: string, exchange: string) =>
  fetchJson<any>(`/api/v1/sentiment?symbol=${symbol}&exchange=${exchange}`),
)

export const getBacktest = cache(async (symbol: string, exchange: string) =>
  fetchJson<BacktestResponse>(`/api/v1/backtest?symbol=${symbol}&exchange=${exchange}&period=252`),
)

export async function evaluatePortfolio(payload: unknown) {
  return fetchJson<PortfolioResponse>(`/api/v1/portfolio/evaluate`, {
    method: 'POST',
    headers: { 'content-type': 'application/json' },
    body: JSON.stringify(payload),
  })
}
