"""Performance metrics for an equity curve.

Pure functions over a list of equity values (one per price step). No numpy
required — the formulae are standard and kept readable on purpose.

Part of Crypto Trading Bot by Viprasol Tech Private Limited (https://viprasol.com).
"""

from __future__ import annotations

import math
from collections.abc import Sequence
from itertools import pairwise


def returns(equity: Sequence[float]) -> list[float]:
    """Step-over-step simple returns of an equity curve."""
    out: list[float] = []
    for prev, cur in pairwise(equity):
        out.append(cur / prev - 1.0 if prev else 0.0)
    return out


def total_return(equity: Sequence[float]) -> float:
    """Total return from first to last equity value."""
    if len(equity) < 2 or equity[0] == 0:
        return 0.0
    return equity[-1] / equity[0] - 1.0


def max_drawdown(equity: Sequence[float]) -> float:
    """Largest peak-to-trough decline as a positive fraction (0.2 == -20%)."""
    peak = -math.inf
    worst = 0.0
    for value in equity:
        peak = max(peak, value)
        if peak > 0:
            worst = max(worst, (peak - value) / peak)
    return worst


def volatility(equity: Sequence[float]) -> float:
    """Sample standard deviation of step returns."""
    rets = returns(equity)
    if len(rets) < 2:
        return 0.0
    mean = sum(rets) / len(rets)
    var = sum((r - mean) ** 2 for r in rets) / (len(rets) - 1)
    return math.sqrt(var)


def sharpe_ratio(equity: Sequence[float], periods_per_year: int = 365) -> float:
    """Annualised Sharpe ratio (risk-free rate assumed zero)."""
    rets = returns(equity)
    if len(rets) < 2:
        return 0.0
    mean = sum(rets) / len(rets)
    vol = volatility(equity)
    if vol == 0:
        return 0.0
    return (mean / vol) * math.sqrt(periods_per_year)


def cagr(equity: Sequence[float], periods_per_year: int = 365) -> float:
    """Compound annual growth rate implied by the curve length."""
    n = len(equity)
    if n < 2 or equity[0] <= 0 or equity[-1] <= 0:
        return 0.0
    years = (n - 1) / periods_per_year
    if years <= 0:
        return 0.0
    return float((equity[-1] / equity[0]) ** (1.0 / years)) - 1.0
