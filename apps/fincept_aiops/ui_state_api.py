from fastapi import APIRouter
from apps.fincept_aiops.state_store import StateStore
from apps.fincept_aiops.audit_logger import AuditLogger

router = APIRouter(tags=["ui"])
state = StateStore()
audit = AuditLogger()


@router.get("/ui/paper-state")
def paper_state():
    return {
        "signal": state.load("latest_signal_candidate"),
        "risk": state.load("latest_risk"),
        "briefing": state.load("latest_briefing"),
        "approval": state.load("latest_approval"),
    }


@router.get("/ui/audit")
def audit_log():
    return {"records": audit.recent(50)}
