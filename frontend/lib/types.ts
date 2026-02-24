export type Exchange = 'NSE' | 'BSE' | 'NASDAQ'

export type OhlcPoint = {
  date: string
  open: number
  high: number
  low: number
  close: number
  volume?: number
}

export type IntelligenceResponse = {
  symbol: string
  exchange: string
  recommendation: string
  confidence: number
  quant_score: number
  fundamental_score: number
  sentiment_score: number
  risk_score: number
  composite_score: number
  summary: string
  risk_level?: 'Low' | 'Medium' | 'High'
  price_history?: OhlcPoint[]
  technicals?: { ma20?: number[]; ma50?: number[]; rsi?: number[] }
  warnings?: string[]
  provenance: { model_version: string }
  benchmark: { active_return: number }
  explainability: { feature_importance: Record<string, number>; feature_notes?: Record<string, string> }
}

export type IntelligenceSummaryResponse = {
  recommendation: string
  confidence: number
  risk_level: string
  top_drivers: string[]
  top_warnings: string[]
  summary: string
}

export type PortfolioStressMetric = {
  name: string
  portfolio_value?: number
  drawdown?: number
  volatility?: number
  var_95?: number
  impact_pct?: number
}

export type PortfolioResponse = {
  weights: Record<string, number>
  expected_return: number
  volatility: number
  sharpe_ratio: number
  var_95?: number
  max_drawdown_proxy?: number
  beta_vs_benchmark?: number
  concentration_index_hhi?: number
  sector_exposure?: Record<string, number>
  stress_tests: PortfolioStressMetric[]
  risk_contribution: Record<string, number>
  expected_asset_returns: Record<string, number>
  correlation_matrix: Record<string, Record<string, number>>
}

export type BacktestTrade = {
  index: number
  signal: string
  asset_return: number
  strategy_return: number
  details?: string
}

export type BacktestResponse = {
  symbol: string
  exchange: Exchange
  period_days: number
  strategy_return: number
  buy_hold_return: number
  active_return: number
  information_ratio: number
  max_drawdown: number
  win_rate: number
  trade_count: number
  avg_return_per_trade: number
  equity_curve: number[]
  benchmark_curve: number[]
  drawdown_curve: number[]
  trade_log: BacktestTrade[]
  benchmark_symbol: string
  schema_version: string
}
