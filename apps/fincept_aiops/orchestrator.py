from typing import Any, Dict
from apps.fincept_aiops.agents.research_agent import ResearchAgent
from apps.fincept_aiops.research_pipeline import ResearchPipeline
from apps.fincept_aiops.agents.briefing_agent import BriefingAgent
from apps.fincept_aiops.agents.audit_agent import AuditAgent
from apps.fincept_aiops.state_store import StateStore


class Orchestrator:
    """
    Flow: research_agent → pipeline (validate→signal→risk→persist) → briefing_agent → audit
    Human approval gate sits between risk evaluation and execution.
    """
    def __init__(self):
        self.researcher = ResearchAgent()
        self.pipeline = ResearchPipeline()
        self.briefing = BriefingAgent()
        self.audit = AuditAgent()
        self.state = StateStore()

    def run_full_cycle(self, symbol: str, timeframe: str = "1d") -> Dict[str, Any]:
        research_result = self.researcher.run(symbol, timeframe)
        if not research_result.get("ok"):
            self.audit.log({"actor": "orchestrator", "action": "research_failed", "symbol": symbol})
            return {"ok": False, "stage": "research", "detail": research_result}
        pipeline_result = self.pipeline.run(research_result["research_note"])
        if not pipeline_result.get("ok"):
            self.audit.log({"actor": "orchestrator", "action": "pipeline_failed",
                            "symbol": symbol, "stage": pipeline_result.get("stage")})
            return {"ok": False, "stage": "pipeline", "detail": pipeline_result}
        briefing = self.briefing.run()
        self.audit.log({"actor": "orchestrator", "action": "full_cycle_complete",
                        "symbol": symbol, "signal_side": pipeline_result["signal_candidate"]["side"],
                        "risk_status": pipeline_result["risk_decision"]["status"]})
        return {"ok": True, "symbol": symbol, "pipeline": pipeline_result, "briefing": briefing}
