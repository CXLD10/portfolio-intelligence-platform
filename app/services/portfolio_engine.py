from __future__ import annotations

import hashlib

import numpy as np

from app.config.settings import settings
from app.integrations.project1_client import Project1Client
from app.integrations.project2_client import Project2Client
from app.models.schemas import PortfolioEvaluateRequest, PortfolioEvaluateResponse, StressScenario
from app.services.benchmark_engine import benchmark_symbol_for_exchange
from app.services.risk_engine import RiskEngine
from app.utils.cache import TTLCache
from app.utils.math_utils import returns_from_prices


class PortfolioEngine:
    def __init__(self) -> None:
        self.p1 = Project1Client()
        self.p2 = Project2Client()
        self.risk = RiskEngine()
        self.cache = TTLCache()

    def _cache_key(self, req: PortfolioEvaluateRequest) -> str:
        raw = "|".join([f"{a.exchange.value}:{a.symbol}:{a.weight}" for a in req.assets]) + f"::{req.weighting_mode}"
        return hashlib.sha1(raw.encode()).hexdigest()

    def _weights(self, req: PortfolioEvaluateRequest, expected: dict[str, float], vol: dict[str, float], conf: dict[str, float], risk: dict[str, float]) -> dict[str, float]:
        symbols = [a.symbol.upper() for a in req.assets]
        if req.weighting_mode == "manual":
            raw = np.array([(a.weight if a.weight is not None else 1.0) for a in req.assets], dtype=float)
        elif req.weighting_mode == "confidence":
            raw = np.array([max(0.01, conf[s]) for s in symbols], dtype=float)
        elif req.weighting_mode == "vol_target":
            raw = np.array([1 / max(0.01, vol[s]) for s in symbols], dtype=float)
        elif req.weighting_mode == "risk_parity":
            raw = np.array([1 / max(0.01, risk[s]) for s in symbols], dtype=float)
        else:
            raw = np.array([max(0.01, expected[s] / max(vol[s], 0.01)) for s in symbols], dtype=float)
        weights = raw / raw.sum()
        return {symbols[i]: float(weights[i]) for i in range(len(symbols))}

    def _stress_tests(self, exp_return: float, vol: float, var95: float) -> list[StressScenario]:
        scenarios = [
            ("market_shock_-10", exp_return - 0.10, vol, var95),
            ("crash_-20", exp_return - 0.20, vol * 1.2, var95 * 1.2),
            ("vol_spike_x1.5", exp_return, vol * 1.5, var95 * 1.5),
            ("corr_spike_0.9", exp_return * 0.92, vol * 1.35, var95 * 1.35),
        ]
        out: list[StressScenario] = []
        for name, sr, sv, vv in scenarios:
            impact = ((sr - exp_return) / max(abs(exp_return), 1e-9)) * 100 if exp_return != 0 else sr * 100
            out.append(StressScenario(name=name, shocked_return=round(sr, 6), shocked_volatility=round(sv, 6), shocked_var_95=round(vv, 6), impact_pct=round(impact, 4)))
        return out

    def evaluate(self, req: PortfolioEvaluateRequest) -> PortfolioEvaluateResponse:
        key = self._cache_key(req)
        cached = self.cache.get(key)
        if cached is not None:
            return cached

        symbols = [a.symbol.upper() for a in req.assets]
        exchanges = {a.symbol.upper(): a.exchange for a in req.assets}

        prices: dict[str, list[float]] = {}
        expected: dict[str, float] = {}
        volatility: dict[str, float] = {}
        confidence: dict[str, float] = {}
        risk_scores: dict[str, float] = {}
        sectors: dict[str, str] = {}
        bench_symbol = benchmark_symbol_for_exchange(exchanges[symbols[0]])
        benchmark = returns_from_prices([x["close"] for x in self.p1.get_historical(bench_symbol, exchanges[symbols[0]], 252)])

        for s in symbols:
            hist = self.p1.get_historical(s, exchanges[s], 252)
            px = [h["close"] for h in hist]
            prices[s] = px
            rets = returns_from_prices(px)
            pred = self.p2.get_prediction(s, exchanges[s])
            fun = self.p1.get_fundamentals(s, exchanges[s])
            expected[s] = float(pred["expected_return"])
            volatility[s] = float(np.std(rets) * np.sqrt(252)) if len(rets) else 0.0
            confidence[s] = float(pred["confidence"])
            risk_scores[s] = float(pred["risk_score"])
            sectors[s] = str(fun["sector"])

        weights = self._weights(req, expected, volatility, confidence, risk_scores)
        w_vec = np.array([weights[s] for s in symbols], dtype=float)
        ret_matrix = np.column_stack([returns_from_prices(prices[s]) for s in symbols])

        exp_return = float(sum(weights[s] * expected[s] for s in symbols))
        vol = self.risk.portfolio_volatility(ret_matrix, w_vec)
        sharpe = float((exp_return - settings.risk_free_rate / 252) / max(vol / np.sqrt(252), 1e-9))
        var95 = self.risk.var95(vol)

        equity = np.cumprod(1 + ret_matrix @ w_vec)
        peaks = np.maximum.accumulate(equity)
        dd = equity / peaks - 1
        max_dd = float(dd.min()) if dd.size else 0.0

        betas = [self.risk.beta(returns_from_prices(prices[s]), benchmark) for s in symbols]
        beta = float(sum(weights[symbols[i]] * betas[i] for i in range(len(symbols))))

        hhi = float(sum(v * v for v in weights.values()))
        sector_exposure: dict[str, float] = {}
        for s, w in weights.items():
            sec = sectors[s]
            sector_exposure[sec] = sector_exposure.get(sec, 0) + w

        corr = self.risk.correlation({s: returns_from_prices(prices[s]).tolist() for s in symbols})
        rc = self.risk.risk_contribution(ret_matrix, w_vec)
        rc_map = {symbols[i]: float(rc[i]) for i in range(len(symbols))}

        out = PortfolioEvaluateResponse(
            weights=weights,
            expected_return=round(exp_return, 6),
            volatility=round(vol, 6),
            sharpe_ratio=round(sharpe, 6),
            var_95=round(var95, 6),
            max_drawdown_proxy=round(max_dd, 6),
            beta_vs_benchmark=round(beta, 6),
            concentration_index_hhi=round(hhi, 6),
            sector_exposure={k: round(v, 6) for k, v in sector_exposure.items()},
            correlation_matrix={k: {kk: round(vv, 6) for kk, vv in v.items()} for k, v in corr.items()},
            risk_contribution={k: round(v, 6) for k, v in rc_map.items()},
            stress_tests=self._stress_tests(exp_return, vol, var95),
            schema_version=settings.schema_version,
        )
        self.cache.set(key, out, settings.portfolio_cache_ttl_s)
        return out
