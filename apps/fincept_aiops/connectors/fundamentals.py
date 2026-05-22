import os
from typing import Any, Dict
from apps.fincept_aiops.connectors.base import BaseConnector


class FundamentalsConnector(BaseConnector):
    name = "fundamentals"

    def fetch(self, params: Dict[str, Any]) -> Dict[str, Any]:
        symbol = str(params.get("symbol", "")).upper()
        if os.getenv("MARKET_DATA_PROVIDER", "stub") == "stub" or not symbol:
            return self._stub(symbol)
        try:
            import yfinance as yf
            info = yf.Ticker(symbol).info or {}
            return {"ok": True, "symbol": symbol, "market_cap": info.get("marketCap"),
                    "pe_ratio": info.get("trailingPE"), "revenue_ttm": info.get("totalRevenue"),
                    "debt_to_equity": info.get("debtToEquity"), "current_ratio": info.get("currentRatio"),
                    "roe": info.get("returnOnEquity"), "sector": info.get("sector")}
        except Exception as e:
            return {"ok": False, "error": str(e), "symbol": symbol}

    def _stub(self, symbol):
        return {"ok": True, "symbol": symbol or "STUB", "market_cap": 3_000_000_000_000,
                "pe_ratio": 28.5, "revenue_ttm": 400_000_000_000, "roe": 0.35,
                "sector": "Technology", "stub": True}
