"""Command-line interface for Crypto Trading Bot.

``crypto-trading-bot demo`` runs a grid or DCA strategy on a synthetic price
series against the simulated exchange — no API keys, no risk.

Part of Crypto Trading Bot by Viprasol Tech Private Limited (https://viprasol.com).
"""

from __future__ import annotations

import math

import typer
from rich.console import Console

from crypto_trading_bot import __version__
from crypto_trading_bot.bot import TradingBot
from crypto_trading_bot.exchanges.simulated import SimulatedExchange
from crypto_trading_bot.strategies.base import Strategy
from crypto_trading_bot.strategies.dca import DCAStrategy
from crypto_trading_bot.strategies.grid import GridStrategy

app = typer.Typer(add_completion=False, help="Crypto Trading Bot — by Viprasol Tech.")
console = Console()


def _synthetic_prices(n: int = 200, base: float = 100.0) -> list[float]:
    return [base + 15.0 * math.sin(i / 10.0) for i in range(n)]


@app.command()
def version() -> None:
    """Print the installed version."""
    console.print(f"crypto-trading-bot [bold cyan]{__version__}[/] — by Viprasol Tech")


@app.command()
def demo(strategy: str = typer.Option("grid", help="grid | dca")) -> None:
    """Run a strategy on synthetic data against the simulated exchange."""
    prices = _synthetic_prices()
    exchange = SimulatedExchange(balances={"USDT": 10_000.0})
    strat: Strategy
    if strategy == "grid":
        strat = GridStrategy(lower=85, upper=115, levels=13, quantity=1.0)
    elif strategy == "dca":
        strat = DCAStrategy(quote_amount=100.0, interval=5)
    else:
        console.print("[red]strategy must be 'grid' or 'dca'[/]")
        raise typer.Exit(code=1)

    bot = TradingBot("BTC/USDT", strat, exchange)
    final = bot.run(prices)
    console.print(f"Strategy:     [bold]{strat.name}[/]")
    console.print(f"Fills:        {len(bot.fills)}")
    console.print(f"Final equity: [bold green]${final:,.2f}[/] (started $10,000.00)")


if __name__ == "__main__":
    app()
