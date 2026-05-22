from typing import Any, Dict
from datetime import datetime
import uuid


class StrategyLab:
    def generate_signal(self, research_note: Dict[str, Any]) -> Dict[str, Any]:
        confidence = float(research_note.get("confidence") or 0)
        if confidence < 0.70:
            return {"status": "no_signal", "reason": "insufficient_confidence"}
        bull = research_note.get("bull_case") or []
        bear = research_note.get("bear_case") or []
        asset = research_note.get("asset", "UNKNOWN")
        if len(bull) >= len(bear):
            side, thesis = "buy", bull[0] if bull else "bullish technical signal"
        else:
            side, thesis = "sell", bear[0] if bear else "bearish technical signal"
        return {
            "signal_id": str(uuid.uuid4()),
            "asset": asset.upper(),
            "side": side,
            "thesis": thesis,
            "confidence": confidence,
            "entry_type": "market",
            "size_pct": 0.05,
            "time_in_force": "day",
            "source_research_id": research_note.get("research_id", ""),
            "created_at": datetime.utcnow().isoformat() + "Z",
        }
