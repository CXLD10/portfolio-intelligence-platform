from __future__ import annotations

import numpy as np

from app.config.settings import settings
from app.models.schemas import Exchange


def benchmark_symbol_for_exchange(exchange: Exchange) -> str:
    if exchange == Exchange.NSE:
        return settings.benchmark_symbol_nse
    if exchange == Exchange.BSE:
        return settings.benchmark_symbol_bse
    return settings.benchmark_symbol_nasdaq


class BenchmarkEngine:
    def compare(self, asset_returns: np.ndarray, benchmark_returns: np.ndarray, benchmark_symbol: str) -> dict:
        n = min(len(asset_returns), len(benchmark_returns))
        if n == 0:
            return {
                "benchmark_symbol": benchmark_symbol,
                "active_return": 0.0,
                "tracking_error": 0.0,
                "information_ratio": 0.0,
                "relative_drawdown": 0.0,
            }
        a = asset_returns[-n:]
        b = benchmark_returns[-n:]
        active_series = a - b
        active_return = float(np.prod(1 + a) - np.prod(1 + b))
        tracking_error = float(np.std(active_series) * np.sqrt(252))
        information_ratio = float((np.mean(active_series) * 252) / tracking_error) if tracking_error > 0 else 0.0

        asset_eq = np.cumprod(1 + a)
        bench_eq = np.cumprod(1 + b)
        asset_dd = np.min(asset_eq / np.maximum.accumulate(asset_eq) - 1)
        bench_dd = np.min(bench_eq / np.maximum.accumulate(bench_eq) - 1)

        return {
            "benchmark_symbol": benchmark_symbol,
            "active_return": round(active_return, 6),
            "tracking_error": round(tracking_error, 6),
            "information_ratio": round(information_ratio, 6),
            "relative_drawdown": round(float(asset_dd - bench_dd), 6),
        }
