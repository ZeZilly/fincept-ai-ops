from typing import Any, Dict
from datetime import datetime
import uuid

from apps.fincept_aiops.validation import (
    validate_research_note, is_valid_confidence, has_minimum_sources
)
from apps.fincept_aiops.strategy_lab import StrategyLab
from apps.fincept_aiops.risk_policy import RiskPolicy
from apps.fincept_aiops.state_store import StateStore
from apps.fincept_aiops.audit_logger import AuditLogger


class ResearchPipeline:
    """Orchestrates: validate → enrich → signal → risk → persist → audit."""

    def __init__(self):
        self.strategy = StrategyLab()
        self.risk = RiskPolicy()
        self.state = StateStore()
        self.audit = AuditLogger()

    def run(self, research_input: Dict[str, Any]) -> Dict[str, Any]:
        # Stage 1 — Contract validation
        errors = validate_research_note(research_input)
        if errors:
            return {"ok": False, "stage": "validate", "errors": errors}

        # Stage 2 — Confidence gate
        if not is_valid_confidence(research_input):
            return {"ok": False, "stage": "confidence", "error": "confidence_below_0.70"}

        # Stage 3 — Source gate
        if not has_minimum_sources(research_input):
            return {"ok": False, "stage": "sources", "error": "minimum_2_sources_required"}

        # Stage 4 — Enrich
        research_input.setdefault("research_id", str(uuid.uuid4()))
        research_input.setdefault("created_at", datetime.utcnow().isoformat() + "Z")

        # Stage 5 — Signal generation
        signal = self.strategy.generate_signal(research_input)
        if signal.get("status") == "no_signal":
            return {"ok": False, "stage": "signal", "error": signal.get("reason")}

        # Stage 6 — Risk evaluation
        order_intent = {
            "asset": signal["asset"],
            "side": signal["side"],
            "thesis": signal["thesis"],
            "size_pct": signal.get("size_pct", 0.05),
        }
        risk_result = self.risk.evaluate(order_intent, {})

        # Stage 7 — Build briefing payload
        briefing = {
            "date": datetime.utcnow().strftime("%Y-%m-%d"),
            "research_summary": research_input.get("summary"),
            "signal": signal,
            "risk": risk_result,
            "pending_actions": (
                ["human_approval_required"] if risk_result["status"] == "approved"
                else ["risk_rejected"]
            ),
        }

        # Stage 8 — Persist artifacts
        self.state.save("latest_signal_candidate", signal)
        self.state.save("latest_risk", risk_result)
        self.state.save("latest_briefing", briefing)

        # Stage 9 — Audit
        self.audit.append({
            "actor": "research_pipeline",
            "action": "pipeline_complete",
            "asset": signal["asset"],
            "side": signal["side"],
            "confidence": research_input.get("confidence"),
            "risk_status": risk_result["status"],
        })

        return {
            "ok": True,
            "research_note": research_input,
            "signal_candidate": signal,
            "risk_decision": risk_result,
            "briefing_packet": briefing,
        }
