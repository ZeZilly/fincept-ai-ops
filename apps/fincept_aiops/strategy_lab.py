from typing import Any, Dict
from datetime import datetime
import uuid


class StrategyLab:
    def generate_signal(self, research_note: Dict[str, Any]) -> Dict[str, Any]:
        confidence = float(research_note.get("confidence", 0))
        bull = research_note.get("bull_case", [])
        bear = research_note.get("bear_case", [])
        asset = research_note.get("asset", "UNKNOWN")

        if confidence >= 0.70 and len(bull) > len(bear):
            side = "buy"
            thesis = bull[0] if bull else "bullish signal"
        elif confidence >= 0.70 and len(bear) >= len(bull):
            side = "sell"
            thesis = bear[0] if bear else "bearish signal"
        else:
            return {"status": "no_signal", "reason": "insufficient_confidence"}

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
