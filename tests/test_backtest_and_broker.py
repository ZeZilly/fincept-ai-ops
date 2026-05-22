from apps.fincept_aiops.backtest_runner import BacktestRunner
from apps.fincept_aiops.paper_broker import PaperBrokerAdapter


def test_backtest_buy_profit():
    runner = BacktestRunner()
    signal = {"signal_id": "t1", "asset": "AAPL", "side": "buy", "size_pct": 0.05}
    result = runner.run(signal, [100.0, 102.0, 105.0, 103.0, 110.0])
    assert result["ok"] is True
    assert result["pnl"] > 0
    assert result["trade_count"] == 1


def test_backtest_sell_profit():
    runner = BacktestRunner()
    signal = {"signal_id": "t2", "asset": "TSLA", "side": "sell", "size_pct": 0.05}
    result = runner.run(signal, [200.0, 195.0, 190.0])
    assert result["ok"] is True
    assert result["pnl"] > 0


def test_backtest_insufficient_data():
    runner = BacktestRunner()
    result = runner.run({"side": "buy", "size_pct": 0.05}, [100.0])
    assert result["ok"] is False


def test_paper_broker_buy_sell_pnl():
    broker = PaperBrokerAdapter()
    broker.submit_order({"asset": "AAPL", "side": "buy", "qty": 10, "price": 150.0})
    broker.submit_order({"asset": "AAPL", "side": "sell", "qty": 10, "price": 155.0})
    assert round(broker.realized_pnl, 2) == 50.0


def test_paper_broker_close_position():
    broker = PaperBrokerAdapter()
    broker.submit_order({"asset": "MSFT", "side": "buy", "qty": 5, "price": 300.0})
    result = broker.close_position("MSFT", 310.0)
    assert result["ok"] is True
    assert result["realized_pnl"] == 50.0


def test_paper_broker_no_position_close():
    broker = PaperBrokerAdapter()
    result = broker.close_position("UNKNOWN", 100.0)
    assert result["ok"] is False
