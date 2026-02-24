from __future__ import annotations

import numpy as np

from app.utils.math_utils import beta as beta_fn, correlation_matrix, parametric_var, rolling_volatility


class RiskEngine:
    def portfolio_volatility(self, returns_matrix: np.ndarray, weights: np.ndarray) -> float:
        if returns_matrix.size == 0:
            return 0.0
        cov = np.cov(returns_matrix.T)
        return float(np.sqrt(weights.T @ cov @ weights) * np.sqrt(252))

    def correlation(self, series_map: dict[str, list[float]]) -> dict[str, dict[str, float]]:
        corr_df = correlation_matrix(series_map)
        return {c: {idx: float(corr_df.loc[idx, c]) for idx in corr_df.index} for c in corr_df.columns}

    def beta(self, asset_returns: np.ndarray, benchmark_returns: np.ndarray) -> float:
        return beta_fn(asset_returns, benchmark_returns)

    def var95(self, volatility_annualized: float) -> float:
        return parametric_var(volatility_annualized, alpha_z=1.65)

    def risk_contribution(self, returns_matrix: np.ndarray, weights: np.ndarray) -> np.ndarray:
        if returns_matrix.size == 0:
            return np.zeros_like(weights)
        cov = np.cov(returns_matrix.T)
        portfolio_var = float(weights.T @ cov @ weights)
        if portfolio_var <= 0:
            return np.zeros_like(weights)
        marginal = cov @ weights
        contrib = weights * marginal / portfolio_var
        return contrib

    def rolling_vol(self, returns: np.ndarray, window: int = 20) -> list[float]:
        return rolling_volatility(returns, window)
