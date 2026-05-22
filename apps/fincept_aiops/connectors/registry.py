from apps.fincept_aiops.connectors.market_data import MarketDataConnector
from apps.fincept_aiops.connectors.fundamentals import FundamentalsConnector
from apps.fincept_aiops.connectors.news import NewsConnector
from apps.fincept_aiops.connectors.backtest_connector import BacktestConnector
from apps.fincept_aiops.connectors.broker_sandbox import BrokerSandboxConnector

ACTIVE_CONNECTORS = {
    "market_data": MarketDataConnector(),
    "fundamentals": FundamentalsConnector(),
    "news": NewsConnector(),
    "backtest": BacktestConnector(),
    "broker_sandbox": BrokerSandboxConnector(),
}


def get_connector(name: str):
    c = ACTIVE_CONNECTORS.get(name)
    if c is None:
        raise KeyError(f"Connector '{name}' not found or disabled.")
    return c
