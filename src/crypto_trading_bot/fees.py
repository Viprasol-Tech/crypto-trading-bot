"""Trading cost model: exchange fees + market-impact slippage.

Real fills are never free and never exactly at the quoted price. ``CostModel``
captures both effects so backtests and paper trades stay honest:

* **Fee** — a proportional taker fee charged on notional (e.g. 0.1%).
* **Slippage** — the price moves against you by ``slippage_bps`` basis points:
  buys fill a touch higher, sells a touch lower.

Part of Crypto Trading Bot by Viprasol Tech Private Limited (https://viprasol.com).
"""

from __future__ import annotations

from dataclasses import dataclass

from crypto_trading_bot.models import Side

BPS = 1e-4  # one basis point


@dataclass(slots=True, frozen=True)
class CostModel:
    """Proportional fee + basis-point slippage applied to every fill.

    Args:
        fee_rate: Proportional taker fee on notional (0.001 == 0.1%).
        slippage_bps: Adverse price move in basis points (10 == 0.10%).
    """

    fee_rate: float = 0.001
    slippage_bps: float = 0.0

    def __post_init__(self) -> None:
        if self.fee_rate < 0:
            raise ValueError("fee_rate must be >= 0")
        if self.slippage_bps < 0:
            raise ValueError("slippage_bps must be >= 0")

    def fill_price(self, side: Side, price: float) -> float:
        """Quoted price adjusted for adverse slippage."""
        slip = price * self.slippage_bps * BPS
        return price + slip if side is Side.BUY else price - slip

    def fee(self, notional: float) -> float:
        """Fee charged on an absolute notional value."""
        return abs(notional) * self.fee_rate
