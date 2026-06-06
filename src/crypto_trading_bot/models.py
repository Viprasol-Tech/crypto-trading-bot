"""Core types for the crypto trading bot.

Part of Crypto Trading Bot by Viprasol Tech Private Limited (https://viprasol.com).
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class Side(str, Enum):
    """Order side."""

    BUY = "buy"
    SELL = "sell"


@dataclass(slots=True, frozen=True)
class Order:
    """A limit or market order."""

    symbol: str
    side: Side
    quantity: float
    price: float


@dataclass(slots=True)
class Fill:
    """A filled order.

    ``fill_price`` is the price actually paid/received after slippage, which can
    differ from the order's quoted ``price``. ``notional`` is signed by side
    (positive cash out for buys, positive cash in for sells, before fees).
    """

    order: Order
    fee: float = 0.0
    fill_price: float | None = None

    def __post_init__(self) -> None:
        if self.fill_price is None:
            self.fill_price = self.order.price

    @property
    def executed_price(self) -> float:
        """The price actually transacted at (after slippage)."""
        assert self.fill_price is not None  # set in __post_init__
        return self.fill_price

    @property
    def notional(self) -> float:
        """Absolute traded value (quantity * executed price), excluding fees."""
        return self.executed_price * self.order.quantity
