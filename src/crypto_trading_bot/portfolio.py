"""Portfolio tracker — realized/unrealized PnL and per-asset positions.

Consumes :class:`~crypto_trading_bot.models.Fill` objects and a mark price to
report cash, holdings, average entry, total fees, and realized vs unrealized PnL.
Uses average-cost accounting (the convention most retail tax/PnL tools use).

Part of Crypto Trading Bot by Viprasol Tech Private Limited (https://viprasol.com).
"""

from __future__ import annotations

from dataclasses import dataclass, field

from crypto_trading_bot.models import Fill, Side


@dataclass(slots=True)
class Position:
    """An average-cost position in a single base asset."""

    quantity: float = 0.0
    avg_price: float = 0.0
    realized_pnl: float = 0.0

    def unrealized_pnl(self, mark: float) -> float:
        return (mark - self.avg_price) * self.quantity


class Portfolio:
    """Tracks cash, positions, fees and PnL from a stream of fills.

    Args:
        cash: Opening quote-currency cash balance.
        quote: Quote asset symbol (for reporting).
    """

    def __init__(self, cash: float = 0.0, quote: str = "USDT") -> None:
        self.starting_cash = cash
        self.cash = cash
        self.quote = quote
        self.total_fees = 0.0
        self.positions: dict[str, Position] = {}

    def _position(self, base: str) -> Position:
        return self.positions.setdefault(base, Position())

    def apply(self, fill: Fill) -> None:
        """Update cash, position and PnL from a single fill."""
        base = fill.order.symbol.split("/")[0]
        pos = self._position(base)
        qty = fill.order.quantity
        price = fill.executed_price
        self.total_fees += fill.fee
        if fill.order.side is Side.BUY:
            self.cash -= fill.notional + fill.fee
            new_qty = pos.quantity + qty
            if new_qty > 0:
                pos.avg_price = (pos.avg_price * pos.quantity + price * qty) / new_qty
            pos.quantity = new_qty
        else:
            self.cash += fill.notional - fill.fee
            pos.realized_pnl += (price - pos.avg_price) * qty
            pos.quantity -= qty
            if abs(pos.quantity) < 1e-12:
                pos.quantity = 0.0

    def realized_pnl(self) -> float:
        return sum(p.realized_pnl for p in self.positions.values())

    def unrealized_pnl(self, marks: dict[str, float]) -> float:
        """Unrealized PnL given mark prices keyed by base asset."""
        return sum(p.unrealized_pnl(marks.get(b, p.avg_price)) for b, p in self.positions.items())

    def equity(self, marks: dict[str, float]) -> float:
        """Total equity = cash + marked value of all positions."""
        holdings = sum(p.quantity * marks.get(b, p.avg_price) for b, p in self.positions.items())
        return self.cash + holdings

    def total_return(self, marks: dict[str, float]) -> float:
        """Total return as a fraction of starting cash."""
        if self.starting_cash <= 0:
            return 0.0
        return self.equity(marks) / self.starting_cash - 1.0


@dataclass(slots=True)
class PortfolioSnapshot:
    """A serialisable point-in-time view of a portfolio."""

    cash: float
    equity: float
    realized_pnl: float
    unrealized_pnl: float
    total_fees: float
    total_return: float
    positions: dict[str, float] = field(default_factory=dict)

    @classmethod
    def of(cls, portfolio: Portfolio, marks: dict[str, float]) -> PortfolioSnapshot:
        return cls(
            cash=portfolio.cash,
            equity=portfolio.equity(marks),
            realized_pnl=portfolio.realized_pnl(),
            unrealized_pnl=portfolio.unrealized_pnl(marks),
            total_fees=portfolio.total_fees,
            total_return=portfolio.total_return(marks),
            positions={b: p.quantity for b, p in portfolio.positions.items() if p.quantity},
        )
