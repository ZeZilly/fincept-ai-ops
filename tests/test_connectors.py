import os
os.environ["MARKET_DATA_PROVIDER"] = "stub"

from apps.fincept_aiops.connectors.market_data import MarketDataConnector
from apps.fincept_aiops.connectors.fundamentals import FundamentalsConnector
from apps.fincept_aiops.connectors.news import NewsConnector
from apps.fincept_aiops.connectors.backtest_connector import BacktestConnector
from apps.fincept_aiops.connectors.broker_sandbox import BrokerSandboxConnector
from apps.fincept_aiops.connectors.registry import get_connector
import pytest


def test_market_data_stub():
    r = MarketDataConnector().fetch({"symbol": "AAPL"})
    assert r["ok"] and r["stub"]


def test_fundamentals_stub():
    r = FundamentalsConnector().fetch({"symbol": "AAPL"})
    assert r["ok"] and "pe_ratio" in r


def test_news_stub():
    r = NewsConnector().fetch({"symbol": "AAPL", "limit": 2})
    assert r["ok"] and len(r["items"]) >= 1


def test_backtest_connector():
    r = BacktestConnector().fetch({"signal": {"side": "buy", "size_pct": 0.05, "asset": "AAPL"}, "price_series": [100.0, 110.0]})
    assert r["ok"] and r["pnl"] > 0


def test_broker_sandbox():
    r = BrokerSandboxConnector().fetch({"action": "submit", "order_intent": {"asset": "AAPL", "side": "buy", "qty": 5, "price": 150.0}})
    assert r["ok"]


def test_registry_get():
    assert get_connector("market_data") is not None


def test_registry_disabled():
    with pytest.raises(KeyError):
        get_connector("live_broker")
