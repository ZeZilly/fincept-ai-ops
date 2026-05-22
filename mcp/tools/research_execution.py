"""MCP tool wrapper — research pipeline execution."""
from apps.fincept_aiops.research_pipeline import ResearchPipeline
from apps.fincept_aiops.state_store import StateStore
from apps.fincept_aiops.audit_logger import AuditLogger

_pipeline = ResearchPipeline()
_state = StateStore()
_audit = AuditLogger()


def run_research_pipeline(research_note: dict) -> dict:
    return _pipeline.run(research_note)


def get_paper_state() -> dict:
    return {
        "signal": _state.load("latest_signal_candidate"),
        "risk": _state.load("latest_risk"),
        "briefing": _state.load("latest_briefing"),
        "approval": _state.load("latest_approval"),
    }


def get_audit_log(n: int = 20) -> dict:
    return {"records": _audit.recent(n)}
