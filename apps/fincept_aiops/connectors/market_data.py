import os
from typing import Any, Dict, List
from apps.fincept_aiops.connectors.base import BaseConnector


class MarketDataConnector(BaseConnector):
    name = "market_data"

    def fetch(self, params: Dict[str, Any]) -> Dict[str, Any]:
        symbol = str(params.get("symbol", "")).upper()
        period = str(params.get("period", "1d"))
        if os.getenv("MARKET_DATA_PROVIDER", "stub") == "stub" or not symbol:
            return self._stub(symbol, period)
        try:
            import yfinance as yf
            hist = yf.Ticker(symbol).history(period=period)
            if hist.empty:
                return {"ok": False, "error": "no_data", "symbol": symbol}
            r = hist.iloc[-1]
            return {"ok": True, "symbol": symbol, "close": round(float(r["Close"]), 4),
                    "open": round(float(r["Open"]), 4), "high": round(float(r["High"]), 4),
                    "low": round(float(r["Low"]), 4), "volume": int(r["Volume"]), "period": period}
        except Exception as e:
            return {"ok": False, "error": str(e), "symbol": symbol}

    def _stub(self, symbol, period):
        return {"ok": True, "symbol": symbol or "STUB", "close": 150.00, "open": 148.50,
                "high": 151.20, "low": 147.80, "volume": 28_500_000, "period": period, "stub": True}

    def watchlist(self, symbols: List[str]):
        return [self.fetch({"symbol": s}) for s in symbols]
