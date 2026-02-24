import { IntelligenceResponse, PortfolioResponse } from './types'
const API = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
export async function getIntelligence(symbol:string, exchange:string){ const r=await fetch(`${API}/api/v1/intelligence?symbol=${symbol}&exchange=${exchange}`,{cache:'no-store'}); if(!r.ok) throw new Error('intelligence failed'); return r.json() as Promise<IntelligenceResponse> }
export async function getMarketOverview(){ const r=await fetch(`${API}/api/v1/market/overview`,{cache:'no-store'}); if(!r.ok) throw new Error('market overview failed'); return r.json() }
export async function getSentiment(symbol:string,exchange:string){ const r=await fetch(`${API}/api/v1/sentiment?symbol=${symbol}&exchange=${exchange}`,{cache:'no-store'}); if(!r.ok) throw new Error('sentiment failed'); return r.json() }
export async function getBacktest(symbol:string,exchange:string){ const r=await fetch(`${API}/api/v1/backtest?symbol=${symbol}&exchange=${exchange}&period=252`,{cache:'no-store'}); if(!r.ok) throw new Error('backtest failed'); return r.json() }
export async function evaluatePortfolio(payload:unknown){ const r=await fetch(`${API}/api/v1/portfolio/evaluate`,{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify(payload)}); if(!r.ok) throw new Error('portfolio failed'); return r.json() as Promise<PortfolioResponse> }
