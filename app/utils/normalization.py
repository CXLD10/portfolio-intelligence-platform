from __future__ import annotations

from datetime import UTC, datetime


def normalize_symbol(symbol: str) -> str:
    return symbol.strip().upper()


def normalize_timestamp(ts: datetime | str | None = None) -> str:
    if ts is None:
        dt = datetime.now(UTC)
    elif isinstance(ts, datetime):
        dt = ts.astimezone(UTC)
    else:
        dt = datetime.fromisoformat(ts.replace("Z", "+00:00")).astimezone(UTC)
    return dt.isoformat()


def clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))
