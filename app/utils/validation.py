from __future__ import annotations

from fastapi import HTTPException


def require_non_empty(value: str, field_name: str) -> None:
    if not value or not value.strip():
        raise HTTPException(status_code=422, detail=f"{field_name} is required")


def filter_valid_numeric_map(values: dict[str, float | int | None]) -> dict[str, float]:
    out: dict[str, float] = {}
    for k, v in values.items():
        if isinstance(v, (int, float)):
            out[k] = float(v)
    return out
