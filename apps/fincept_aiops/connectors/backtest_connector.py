from typing import Any, Dict
from apps.fincept_aiops.connectors.base import BaseConnector
from apps.fincept_aiops.backtest_runner import BacktestRunner


class BacktestConnector(BaseConnector):
    name = "backtest"

    def __init__(self):
        self.runner = BacktestRunner()

    def fetch(self, params: Dict[str, Any]) -> Dict[str, Any]:
        return self.runner.run(params.get("signal", {}), params.get("price_series", []),
                               float(params.get("initial_equity", 10_000.0)))
