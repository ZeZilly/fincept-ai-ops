from apps.fincept_aiops.backtest_runner import BacktestRunner
from apps.fincept_aiops.paper_broker import PaperBrokerAdapter


def test_backtest_basic():
    runner = BacktestRunner()
    signal = {"signal_id": "test", "asset": "AAPL", "side": "buy", "size_pct": 0.05}
    prices = [100.0, 102.0, 105.0, 103.0, 107.0]
    result = runner.run(signal, prices)
    assert result["trade_count"] == 1
    assert result["ending_equity"] > 10000


def test_paper_broker_buy_sell():
    broker = PaperBrokerAdapter()
    buy = broker.submit_order({"asset": "AAPL", "side": "buy", "qty": 10, "price": 150.0})
    assert buy["ok"] is True
    sell = broker.submit_order({"asset": "AAPL", "side": "sell", "qty": 10, "price": 155.0})
    assert sell["ok"] is True
    assert broker.realized_pnl == 50.0
