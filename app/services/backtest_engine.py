from __future__ import annotations

import numpy as np

from app.config.settings import settings
from app.integrations.project1_client import Project1Client
from app.integrations.project2_client import Project2Client
from app.models.schemas import BacktestResponse, Exchange
from app.services.benchmark_engine import benchmark_symbol_for_exchange
from app.utils.math_utils import returns_from_prices


class BacktestEngine:
    def __init__(self) -> None:
        self.p1 = Project1Client()
        self.p2 = Project2Client()

    def run(self, symbol: str, exchange: Exchange, period_days: int) -> BacktestResponse:
        hist = self.p1.get_historical(symbol, exchange, period_days)
        closes = [h["close"] for h in hist]
        rets = returns_from_prices(closes)

        bench_symbol = benchmark_symbol_for_exchange(exchange)
        try:
            bench_hist = self.p1.get_historical(bench_symbol, exchange, period_days)
            bench_rets = returns_from_prices([h["close"] for h in bench_hist])
        except Exception:
            bench_rets = np.zeros_like(rets)

        signal_seed = self.p2.get_prediction(symbol, exchange)
        bias = 1 if signal_seed["prediction"] == "BUY" else -1 if signal_seed["prediction"] == "SELL" else 0

        signals = []
        for r in rets:
            momentum = np.sign(r)
            sig = 1 if momentum + bias >= 1 else 0
            signals.append(sig)

        strat_rets = np.array([rets[i] * signals[i] for i in range(len(rets))], dtype=float)
        n = min(len(strat_rets), len(bench_rets), len(rets), len(signals))
        strat_rets = strat_rets[-n:] if n else np.array([], dtype=float)
        bench_rets = bench_rets[-n:] if n else np.array([], dtype=float)
        aligned_rets = rets[-n:] if n else np.array([], dtype=float)
        aligned_signals = signals[-n:] if n else []
        equity = np.cumprod(np.insert(1 + strat_rets, 0, 1.0))
        benchmark_equity = np.cumprod(np.insert(1 + bench_rets, 0, 1.0))
        peaks = np.maximum.accumulate(equity)
        dd_curve = equity / peaks - 1
        trades = [
            {
                "index": i,
                "signal": "BUY" if int(aligned_signals[i]) == 1 else "FLAT",
                "asset_return": float(round(aligned_rets[i], 6)),
                "strategy_return": float(round(strat_rets[i], 6)),
                "details": f"Momentum={round(float(np.sign(aligned_rets[i])), 2)}, Bias={bias}",
            }
            for i in range(len(strat_rets))
            if aligned_signals[i] != 0
        ]

        wins = float(np.sum(strat_rets > 0))
        count = float(max(len(strat_rets), 1))
        active_return = float(np.prod(1 + strat_rets) - np.prod(1 + bench_rets)) if len(strat_rets) else 0.0
        tracking_error = float(np.std(strat_rets - bench_rets) * np.sqrt(252)) if len(strat_rets) else 0.0
        information_ratio = float((np.mean(strat_rets - bench_rets) * 252) / max(tracking_error, 1e-9)) if len(strat_rets) else 0.0

        return BacktestResponse(
            symbol=symbol,
            exchange=exchange,
            period_days=period_days,
            strategy_return=float(round(np.prod(1 + strat_rets) - 1, 6)),
            buy_hold_return=float(round(np.prod(1 + bench_rets) - 1, 6)),
            active_return=float(round(active_return, 6)),
            information_ratio=float(round(information_ratio, 6)),
            max_drawdown=float(round(np.min(dd_curve), 6)),
            win_rate=float(round(wins / count, 6)),
            trade_count=int(len(trades)),
            avg_return_per_trade=float(round(np.mean(strat_rets) if len(strat_rets) else 0.0, 6)),
            equity_curve=[float(round(v, 6)) for v in equity.tolist()],
            benchmark_curve=[float(round(v, 6)) for v in benchmark_equity.tolist()],
            drawdown_curve=[float(round(v, 6)) for v in dd_curve.tolist()],
            trade_log=trades,
            benchmark_symbol=bench_symbol,
            schema_version=settings.schema_version,
        )
