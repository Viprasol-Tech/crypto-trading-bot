"""Tests for the backtest engine, config/registry, data and CLI."""

from __future__ import annotations

import pytest
from typer.testing import CliRunner

from crypto_trading_bot.backtest import run_backtest
from crypto_trading_bot.cli import app
from crypto_trading_bot.config import (
    BotConfig,
    available_strategies,
    build_strategy,
)
from crypto_trading_bot.data import make_series, trending
from crypto_trading_bot.fees import CostModel

runner = CliRunner()


def test_registry_lists_all_five_strategies() -> None:
    names = available_strategies()
    assert set(names) == {"grid", "dca", "momentum", "mean_reversion", "breakout"}


def test_build_strategy_uses_defaults_and_overrides() -> None:
    strat = build_strategy("momentum", {"fast": 5})
    assert strat.name == "momentum"


def test_build_strategy_unknown_raises() -> None:
    with pytest.raises(ValueError):
        build_strategy("nope")


def test_bot_config_validates_symbol_and_strategy() -> None:
    cfg = BotConfig(symbol="BTC/USDT", strategy="grid")
    assert cfg.build().name == "grid"
    with pytest.raises(ValueError):
        BotConfig(symbol="BTCUSDT")
    with pytest.raises(ValueError):
        BotConfig(strategy="bogus")


def test_cost_config_builds_model() -> None:
    cfg = BotConfig(costs={"fee_rate": 0.002, "slippage_bps": 7})
    model = cfg.costs.to_model()
    assert isinstance(model, CostModel)
    assert model.fee_rate == 0.002


def test_run_backtest_produces_coherent_report() -> None:
    prices = trending(n=200, seed=7)
    report = run_backtest(build_strategy("momentum"), prices, cost_model=CostModel(slippage_bps=5))
    assert report.bars == 200
    assert report.n_trades == report.n_buys + report.n_sells
    assert len(report.equity_curve) == 200
    assert 0.0 <= report.win_rate <= 1.0
    assert report.max_drawdown >= 0.0
    d = report.as_dict()
    assert d["strategy"] == "momentum"
    assert "alpha" in d


def test_run_backtest_empty_prices_raises() -> None:
    with pytest.raises(ValueError):
        run_backtest(build_strategy("dca"), [])


def test_buy_and_hold_matches_first_last() -> None:
    prices = [100.0, 110.0, 121.0]
    report = run_backtest(build_strategy("dca", {"interval": 1}), prices)
    assert abs(report.buy_and_hold_return - 0.21) < 1e-9


def test_make_series_kinds() -> None:
    assert len(make_series("sine", 50)) == 50
    assert len(make_series("trend", 30)) == 30
    assert len(make_series("random", 10)) == 10
    with pytest.raises(ValueError):
        make_series("nope")


def test_cli_version() -> None:
    result = runner.invoke(app, ["version"])
    assert result.exit_code == 0
    assert "crypto-trading-bot" in result.stdout


def test_cli_strategies_lists_all() -> None:
    result = runner.invoke(app, ["strategies"])
    assert result.exit_code == 0
    assert "momentum" in result.stdout
    assert "breakout" in result.stdout


def test_cli_demo_runs() -> None:
    result = runner.invoke(app, ["demo", "--strategy", "grid", "--series", "sine"])
    assert result.exit_code == 0
    assert "Final equity" in result.stdout


def test_cli_demo_rejects_bad_strategy() -> None:
    result = runner.invoke(app, ["demo", "--strategy", "nope"])
    assert result.exit_code == 1


def test_cli_backtest_json() -> None:
    result = runner.invoke(
        app, ["backtest", "--strategy", "momentum", "--series", "trend", "--json"]
    )
    assert result.exit_code == 0
    assert "total_return" in result.stdout


def test_cli_compare_ranks() -> None:
    result = runner.invoke(app, ["compare", "--series", "trend", "--bars", "150"])
    assert result.exit_code == 0
    assert "Buy & hold baseline" in result.stdout
