import os
os.environ["MARKET_DATA_PROVIDER"] = "stub"

from apps.fincept_aiops.connectors.market_data import MarketDataConnector
from apps.fincept_aiops.connectors.fundamentals import FundamentalsConnector
from apps.fincept_aiops.connectors.news import NewsConnector
from apps.fincept_aiops.connectors.backtest_connector import BacktestConnector
from apps.fincept_aiops.connectors.broker_sandbox import BrokerSandboxConnector
from apps.fincept_aiops.connectors.registry import get_connector


def test_market_data_stub():
    c = MarketDataConnector()
    r = c.fetch({"symbol": "AAPL"})
    assert r["ok"] is True
    assert r["stub"] is True
    assert "close" in r


def test_fundamentals_stub():
    c = FundamentalsConnector()
    r = c.fetch({"symbol": "AAPL"})
    assert r["ok"] is True
    assert "pe_ratio" in r


def test_news_stub():
    c = NewsConnector()
    r = c.fetch({"symbol": "AAPL", "limit": 2})
    assert r["ok"] is True
    assert len(r["items"]) >= 1


def test_backtest_connector():
    c = BacktestConnector()
    r = c.fetch({
        "signal": {"side": "buy", "size_pct": 0.05, "asset": "AAPL"},
        "price_series": [100.0, 105.0, 110.0],
    })
    assert r["ok"] is True
    assert r["pnl"] > 0


def test_broker_sandbox_connector():
    c = BrokerSandboxConnector()
    r = c.fetch({"action": "submit", "order_intent": {
        "asset": "AAPL", "side": "buy", "qty": 5, "price": 150.0
    }})
    assert r["ok"] is True


def test_registry_get():
    conn = get_connector("market_data")
    assert conn is not None


def test_registry_disabled():
    import pytest
    with pytest.raises(KeyError):
        get_connector("live_broker")
