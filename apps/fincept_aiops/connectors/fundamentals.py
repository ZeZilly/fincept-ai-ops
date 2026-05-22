import os
from typing import Any, Dict
from apps.fincept_aiops.connectors.base import BaseConnector


class FundamentalsConnector(BaseConnector):
    """Connector 2/5 — balance sheet, income, cash flow.
    Provider: yfinance (stub-ready).
    """
    name = "fundamentals"

    def fetch(self, params: Dict[str, Any]) -> Dict[str, Any]:
        provider = os.getenv("MARKET_DATA_PROVIDER", "stub")
        symbol = str(params.get("symbol", "")).upper()

        if provider == "stub" or not symbol:
            return self._stub(symbol)

        try:
            import yfinance as yf
            ticker = yf.Ticker(symbol)
            info = ticker.info or {}
            return {
                "ok": True,
                "symbol": symbol,
                "market_cap": info.get("marketCap"),
                "pe_ratio": info.get("trailingPE"),
                "revenue_ttm": info.get("totalRevenue"),
                "gross_profit_ttm": info.get("grossProfits"),
                "debt_to_equity": info.get("debtToEquity"),
                "current_ratio": info.get("currentRatio"),
                "roe": info.get("returnOnEquity"),
                "sector": info.get("sector"),
                "industry": info.get("industry"),
            }
        except Exception as e:
            return {"ok": False, "error": str(e), "symbol": symbol}

    def _stub(self, symbol: str) -> Dict[str, Any]:
        return {
            "ok": True, "symbol": symbol or "STUB",
            "market_cap": 3_000_000_000_000, "pe_ratio": 28.5,
            "revenue_ttm": 400_000_000_000, "gross_profit_ttm": 170_000_000_000,
            "debt_to_equity": 1.5, "current_ratio": 1.2, "roe": 0.35,
            "sector": "Technology", "industry": "Consumer Electronics", "stub": True,
        }
