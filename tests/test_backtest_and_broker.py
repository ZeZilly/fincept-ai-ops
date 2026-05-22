from apps.fincept_aiops.backtest_runner import BacktestRunner
from apps.fincept_aiops.paper_broker import PaperBrokerAdapter


def test_backtest_buy_profit():
    r = BacktestRunner().run({"asset": "AAPL", "side": "buy", "size_pct": 0.05}, [100.0, 110.0])
    assert r["ok"] and r["pnl"] > 0


def test_backtest_sell_profit():
    r = BacktestRunner().run({"asset": "TSLA", "side": "sell", "size_pct": 0.05}, [200.0, 190.0])
    assert r["ok"] and r["pnl"] > 0


def test_backtest_insufficient_data():
    assert BacktestRunner().run({"side": "buy", "size_pct": 0.05}, [100.0])["ok"] is False


def test_paper_broker_pnl():
    b = PaperBrokerAdapter()
    b.submit_order({"asset": "AAPL", "side": "buy", "qty": 10, "price": 150.0})
    b.submit_order({"asset": "AAPL", "side": "sell", "qty": 10, "price": 155.0})
    assert round(b.realized_pnl, 2) == 50.0


def test_paper_broker_close():
    b = PaperBrokerAdapter()
    b.submit_order({"asset": "MSFT", "side": "buy", "qty": 5, "price": 300.0})
    r = b.close_position("MSFT", 310.0)
    assert r["ok"] and r["realized_pnl"] == 50.0


def test_paper_broker_no_position():
    assert PaperBrokerAdapter().close_position("UNKNOWN", 100.0)["ok"] is False
