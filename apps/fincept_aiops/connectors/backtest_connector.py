from typing import Any, Dict, List
from apps.fincept_aiops.connectors.base import BaseConnector
from apps.fincept_aiops.backtest_runner import BacktestRunner


class BacktestConnector(BaseConnector):
    """Connector 4/5 — signal test and performance analysis."""
    name = "backtest"

    def __init__(self):
        self.runner = BacktestRunner()

    def fetch(self, params: Dict[str, Any]) -> Dict[str, Any]:
        signal = params.get("signal", {})
        price_series = params.get("price_series", [])
        initial_equity = float(params.get("initial_equity", 10_000.0))
        return self.runner.run(signal, price_series, initial_equity)
