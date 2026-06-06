"""A simulated exchange for paper trading and backtests.

Holds balances per asset and fills orders instantly at the current price (set by
the caller or a price feed), applying a :class:`~crypto_trading_bot.fees.CostModel`
for realistic fees and slippage. Symbols are ``BASE/QUOTE`` (e.g. ``BTC/USDT``).

Part of Crypto Trading Bot by Viprasol Tech Private Limited (https://viprasol.com).
"""

from __future__ import annotations

from crypto_trading_bot.exchanges.base import Exchange
from crypto_trading_bot.fees import CostModel
from crypto_trading_bot.models import Fill, Order, Side


class InsufficientFunds(Exception):
    """Raised when an order cannot be afforded with the current balances."""


class SimulatedExchange(Exchange):
    """In-memory exchange with a configurable cost model and balances.

    Args:
        balances: Opening balances per asset (e.g. ``{"USDT": 10_000}``).
        fee_rate: Convenience shortcut to build a default :class:`CostModel`.
            Ignored if ``cost_model`` is supplied.
        cost_model: Full fee + slippage model. Overrides ``fee_rate``.
        allow_short: If ``False`` (default), orders that would drive the base or
            quote balance negative raise :class:`InsufficientFunds`.
    """

    def __init__(
        self,
        balances: dict[str, float] | None = None,
        fee_rate: float = 0.001,
        cost_model: CostModel | None = None,
        allow_short: bool = False,
    ) -> None:
        self._balances: dict[str, float] = dict(balances or {})
        self._prices: dict[str, float] = {}
        self.cost_model = cost_model or CostModel(fee_rate=fee_rate)
        self.allow_short = allow_short

    @property
    def fee_rate(self) -> float:
        """Proportional fee rate from the active cost model."""
        return self.cost_model.fee_rate

    def set_price(self, symbol: str, price: float) -> None:
        """Update the current price used for fills/quotes."""
        self._prices[symbol] = price

    def price(self, symbol: str) -> float:
        return self._prices.get(symbol, 0.0)

    def balance(self, asset: str) -> float:
        return self._balances.get(asset, 0.0)

    @property
    def balances(self) -> dict[str, float]:
        """A copy of all non-trivial balances."""
        return {a: b for a, b in self._balances.items() if abs(b) > 1e-12}

    def execute(self, order: Order) -> Fill:
        base, quote = order.symbol.split("/")
        fill_price = self.cost_model.fill_price(order.side, order.price)
        notional = fill_price * order.quantity
        fee = self.cost_model.fee(notional)
        if order.side is Side.BUY:
            cost = notional + fee
            if not self.allow_short and cost > self.balance(quote) + 1e-9:
                raise InsufficientFunds(f"need {cost:.2f} {quote}, have {self.balance(quote):.2f}")
            self._balances[quote] = self.balance(quote) - cost
            self._balances[base] = self.balance(base) + order.quantity
        else:
            if not self.allow_short and order.quantity > self.balance(base) + 1e-9:
                raise InsufficientFunds(
                    f"need {order.quantity:.8f} {base}, have {self.balance(base):.8f}"
                )
            self._balances[base] = self.balance(base) - order.quantity
            self._balances[quote] = self.balance(quote) + notional - fee
        return Fill(order=order, fee=fee, fill_price=fill_price)

    def equity(self, quote: str = "USDT") -> float:
        """Total equity valued in the quote asset at current prices."""
        total = self.balance(quote)
        for symbol, price in self._prices.items():
            base = symbol.split("/")[0]
            total += self.balance(base) * price
        return total
