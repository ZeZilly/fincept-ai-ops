"""MCP tool wrapper — market data."""
from apps.fincept_aiops.connectors.registry import get_connector


def get_market_data(symbol: str, period: str = "1d") -> dict:
    return get_connector("market_data").fetch({"symbol": symbol, "period": period})


def get_fundamentals(symbol: str) -> dict:
    return get_connector("fundamentals").fetch({"symbol": symbol})


def get_news(symbol: str, limit: int = 5) -> dict:
    return get_connector("news").fetch({"symbol": symbol, "limit": limit})
