"""Command-line interface for Crypto Trading Bot.

Subcommands:

* ``version``     — print the installed version.
* ``strategies``  — list built-in strategies and their default params.
* ``demo``        — run one strategy on a synthetic series (quick look).
* ``backtest``    — full backtest with a metrics report (return, drawdown, Sharpe).
* ``compare``     — backtest every strategy on the same series and rank them.

No API keys, no risk — everything runs on the bundled simulated exchange.

Part of Crypto Trading Bot by Viprasol Tech Private Limited (https://viprasol.com).
"""

from __future__ import annotations

import json

import typer
from rich.console import Console
from rich.table import Table

from crypto_trading_bot import __version__
from crypto_trading_bot.backtest import BacktestReport, run_backtest
from crypto_trading_bot.config import (
    DEFAULT_PARAMS,
    available_strategies,
    build_strategy,
)
from crypto_trading_bot.data import SERIES, make_series
from crypto_trading_bot.fees import CostModel

app = typer.Typer(add_completion=False, help="Crypto Trading Bot - by Viprasol Tech.")
console = Console()


def _pct(value: float) -> str:
    return f"{value * 100:+.2f}%"


def _render_report(report: BacktestReport) -> None:
    table = Table(title=f"Backtest - {report.strategy} on {report.symbol}", title_style="bold cyan")
    table.add_column("Metric", style="bold")
    table.add_column("Value", justify="right")
    table.add_row("Bars", str(report.bars))
    table.add_row("Final equity", f"${report.final_equity:,.2f}")
    table.add_row("Total return", _pct(report.total_return))
    table.add_row("Buy & hold", _pct(report.buy_and_hold_return))
    table.add_row("Alpha vs B&H", _pct(report.alpha))
    table.add_row("Max drawdown", _pct(report.max_drawdown))
    table.add_row("Sharpe (ann.)", f"{report.sharpe:.2f}")
    table.add_row("CAGR", _pct(report.cagr))
    table.add_row("Trades", f"{report.n_trades} ({report.n_buys} buy / {report.n_sells} sell)")
    table.add_row("Win rate", _pct(report.win_rate))
    table.add_row("Total fees", f"${report.total_fees:,.2f}")
    console.print(table)


@app.command()
def version() -> None:
    """Print the installed version."""
    console.print(f"crypto-trading-bot [bold cyan]{__version__}[/] - by Viprasol Tech")


@app.command()
def strategies() -> None:
    """List built-in strategies and their default parameters."""
    table = Table(title="Built-in strategies", title_style="bold cyan")
    table.add_column("Name", style="bold green")
    table.add_column("Default parameters")
    for name in available_strategies():
        params = ", ".join(f"{k}={v}" for k, v in DEFAULT_PARAMS.get(name, {}).items())
        table.add_row(name, params or "-")
    console.print(table)


@app.command()
def demo(
    strategy: str = typer.Option("grid", help=f"One of: {', '.join(available_strategies())}"),
    series: str = typer.Option("sine", help=f"Price series: {', '.join(SERIES)}"),
    bars: int = typer.Option(200, help="Number of price bars."),
) -> None:
    """Run a strategy on a synthetic series and print a quick summary."""
    if strategy not in available_strategies():
        console.print(f"[red]unknown strategy {strategy!r}[/]; try one of {available_strategies()}")
        raise typer.Exit(code=1)
    prices = make_series(series, bars)
    report = run_backtest(build_strategy(strategy), prices)
    console.print(f"Strategy:     [bold]{report.strategy}[/] on [bold]{series}[/] ({bars} bars)")
    console.print(f"Fills:        {report.n_trades}")
    console.print(
        f"Final equity: [bold green]${report.final_equity:,.2f}[/] "
        f"(started ${report.starting_equity:,.2f}, {_pct(report.total_return)})"
    )


@app.command()
def backtest(
    strategy: str = typer.Option("momentum", help=f"One of: {', '.join(available_strategies())}"),
    series: str = typer.Option("trend", help=f"Price series: {', '.join(SERIES)}"),
    bars: int = typer.Option(300, help="Number of price bars."),
    cash: float = typer.Option(10_000.0, help="Starting quote-currency cash."),
    fee_rate: float = typer.Option(0.001, help="Taker fee rate (0.001 == 0.1%)."),
    slippage_bps: float = typer.Option(5.0, help="Slippage in basis points."),
    as_json: bool = typer.Option(False, "--json", help="Emit headline metrics as JSON."),
) -> None:
    """Run a full backtest and print a metrics report."""
    if strategy not in available_strategies():
        console.print(f"[red]unknown strategy {strategy!r}[/]; try one of {available_strategies()}")
        raise typer.Exit(code=1)
    prices = make_series(series, bars)
    costs = CostModel(fee_rate=fee_rate, slippage_bps=slippage_bps)
    report = run_backtest(build_strategy(strategy), prices, cash=cash, cost_model=costs)
    if as_json:
        console.print_json(json.dumps(report.as_dict()))
    else:
        _render_report(report)


@app.command()
def compare(
    series: str = typer.Option("trend", help=f"Price series: {', '.join(SERIES)}"),
    bars: int = typer.Option(300, help="Number of price bars."),
    cash: float = typer.Option(10_000.0, help="Starting quote-currency cash."),
    fee_rate: float = typer.Option(0.001, help="Taker fee rate."),
    slippage_bps: float = typer.Option(5.0, help="Slippage in basis points."),
) -> None:
    """Backtest every strategy on the same series and rank by total return."""
    prices = make_series(series, bars)
    costs = CostModel(fee_rate=fee_rate, slippage_bps=slippage_bps)
    reports = [
        run_backtest(build_strategy(name), prices, cash=cash, cost_model=costs)
        for name in available_strategies()
    ]
    reports.sort(key=lambda r: r.total_return, reverse=True)
    table = Table(title=f"Strategy comparison - {series} ({bars} bars)", title_style="bold cyan")
    table.add_column("Rank", justify="right")
    table.add_column("Strategy", style="bold green")
    table.add_column("Return", justify="right")
    table.add_column("Alpha", justify="right")
    table.add_column("MaxDD", justify="right")
    table.add_column("Sharpe", justify="right")
    table.add_column("Trades", justify="right")
    for rank, report in enumerate(reports, start=1):
        table.add_row(
            str(rank),
            report.strategy,
            _pct(report.total_return),
            _pct(report.alpha),
            _pct(report.max_drawdown),
            f"{report.sharpe:.2f}",
            str(report.n_trades),
        )
    console.print(table)
    console.print(f"Buy & hold baseline: [bold]{_pct(reports[0].buy_and_hold_return)}[/]")


if __name__ == "__main__":
    app()
