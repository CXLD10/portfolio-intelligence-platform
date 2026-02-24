import json
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, urlparse

from app.config.settings import settings
from app.models.schemas import Exchange
from app.services.intelligence_orchestrator import IntelligenceOrchestrator


class _Handler(BaseHTTPRequestHandler):
    def _send(self, payload, code=200):
        body = json.dumps(payload).encode()
        self.send_response(code)
        self.send_header('content-type', 'application/json')
        self.send_header('content-length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format, *args):
        return

    def do_GET(self):
        p = urlparse(self.path)
        q = parse_qs(p.query)
        symbol = q.get('symbol', ['AAPL'])[0]
        exchange = q.get('exchange', ['NASDAQ'])[0]
        if p.path.endswith('/quote'):
            return self._send({"symbol": symbol, "exchange": exchange, "price": 100.0, "volume": 12345, "currency": "USD", "timestamp": "2026-01-01T00:00:00+00:00"})
        if p.path.endswith('/fundamentals'):
            return self._send({"market_cap": 1000000000.0, "sector": "Technology", "industry": "Software", "debt_to_equity": 0.6, "roe": 0.2, "revenue_growth": 0.15})
        if p.path.endswith('/historical'):
            candles = [{"timestamp": f"2026-01-{i+1:02d}T00:00:00+00:00", "close": 100 + i} for i in range(40)]
            return self._send({"candles": candles})
        if p.path.endswith('/market-status'):
            return self._send({"exchange": exchange, "session": "OPEN", "is_open": True})
        if p.path.endswith('/prediction'):
            return self._send({"prediction": "BUY", "confidence": 0.8, "probability_up": 0.8, "probability_down": 0.2, "expected_return": 0.03, "risk_score": 0.4, "forecast_horizon": "5d", "model_version": "v2"})
        if p.path.endswith('/features'):
            return self._send({"volatility": 0.2, "sharpe_ratio": 1.1, "beta": 1.0, "drawdown": -0.1})
        if p.path.endswith('/risk'):
            return self._send({"risk_score": 0.42})
        self._send({"error": "not_found"}, code=404)


def _start_server(port: int):
    server = HTTPServer(('127.0.0.1', port), _Handler)
    t = threading.Thread(target=server.serve_forever, daemon=True)
    t.start()
    return server


def test_full_orchestration_over_http() -> None:
    p1 = _start_server(19001)
    p2 = _start_server(19002)
    try:
        settings.p1_base_url = 'http://127.0.0.1:19001'
        settings.p2_base_url = 'http://127.0.0.1:19002'
        orch = IntelligenceOrchestrator()
        out = orch.run('AAPL', Exchange.NASDAQ)
        assert out.provenance.model_version == 'v2'
        assert out.degraded is False
        assert out.exchange == Exchange.NASDAQ
    finally:
        p1.shutdown()
        p2.shutdown()
