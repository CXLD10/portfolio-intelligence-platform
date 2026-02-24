from __future__ import annotations

import numpy as np
import pandas as pd


def returns_from_prices(prices: list[float]) -> np.ndarray:
    s = pd.Series(prices, dtype=float)
    r = s.pct_change().dropna()
    return r.to_numpy()


def rolling_volatility(returns: np.ndarray, window: int = 20) -> list[float]:
    if len(returns) == 0:
        return []
    s = pd.Series(returns)
    return (s.rolling(window=window, min_periods=1).std(ddof=0) * np.sqrt(252)).fillna(0).tolist()


def correlation_matrix(series_map: dict[str, list[float]]) -> pd.DataFrame:
    frame = pd.DataFrame(series_map)
    return frame.corr().fillna(0)


def beta(asset_returns: np.ndarray, benchmark_returns: np.ndarray) -> float:
    n = min(len(asset_returns), len(benchmark_returns))
    if n < 2:
        return 0.0
    a = asset_returns[-n:]
    b = benchmark_returns[-n:]
    var_b = float(np.var(b))
    if var_b == 0:
        return 0.0
    return float(np.cov(a, b)[0, 1] / var_b)


def parametric_var(volatility_annualized: float, alpha_z: float = 1.65) -> float:
    return float(alpha_z * volatility_annualized / np.sqrt(252))
