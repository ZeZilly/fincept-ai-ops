from typing import Any, Dict
from apps.fincept_aiops.connectors.registry import get_connector
from apps.fincept_aiops.audit_logger import AuditLogger

audit = AuditLogger()


class ResearchAgent:
    """Agent 1 — pulls market + news + fundamentals, builds research note."""

    def run(self, symbol: str, timeframe: str = "1d") -> Dict[str, Any]:
        market = get_connector("market_data").fetch({"symbol": symbol, "period": timeframe})
        news = get_connector("news").fetch({"symbol": symbol, "limit": 5})
        fundamentals = get_connector("fundamentals").fetch({"symbol": symbol})

        if not market.get("ok"):
            return {"ok": False, "error": "market_data_unavailable", "symbol": symbol}

        close = market.get("close", 0)
        prev_open = market.get("open", close)
        price_change_pct = round((close - prev_open) / prev_open * 100, 4) if prev_open else 0

        bull_case = []
        bear_case = []
        key_risks = []

        # Fundamental signals
        pe = fundamentals.get("pe_ratio")
        roe = fundamentals.get("roe")
        if pe and pe < 25:
            bull_case.append(f"PE ratio {pe} below 25 — reasonable valuation")
        if pe and pe > 40:
            bear_case.append(f"PE ratio {pe} above 40 — stretched valuation")
        if roe and roe > 0.20:
            bull_case.append(f"ROE {round(roe*100,1)}% above 20% — strong returns")

        # Price signals
        if price_change_pct > 1.0:
            bull_case.append(f"Price up {price_change_pct}% today — positive momentum")
        elif price_change_pct < -1.0:
            bear_case.append(f"Price down {abs(price_change_pct)}% today — negative momentum")

        # News signals
        news_items = news.get("items", [])
        for item in news_items[:2]:
            title = item.get("title", "")
            if any(w in title.lower() for w in ["beat", "growth", "expand", "record", "profit"]):
                bull_case.append(f"News: {title}")
            elif any(w in title.lower() for w in ["miss", "decline", "loss", "recall", "risk"]):
                bear_case.append(f"News: {title}")

        key_risks.append("macro rate environment")
        if not bull_case and not bear_case:
            bear_case.append("insufficient directional signal")

        confidence = min(0.90, 0.55 + len(bull_case) * 0.08 + len(bear_case) * 0.03)
        sources = ["market_data", "news"]
        if fundamentals.get("ok"):
            sources.append("fundamentals")

        note = {
            "asset": symbol.upper(),
            "timeframe": timeframe,
            "summary": f"{symbol.upper()} closed at {close}. Price change: {price_change_pct}%. PE: {pe}. ROE: {roe}.",
            "bull_case": bull_case,
            "bear_case": bear_case,
            "key_risks": key_risks,
            "confidence": round(confidence, 3),
            "sources_checked": sources,
            "market_snapshot": market,
            "fundamentals_snapshot": fundamentals,
            "news_snapshot": news_items[:3],
        }
        audit.append({"actor": "research_agent", "action": "research_note_built", "asset": symbol.upper()})
        return {"ok": True, "research_note": note}
