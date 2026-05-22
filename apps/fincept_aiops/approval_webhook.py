import os
from datetime import datetime
from fastapi import APIRouter, HTTPException, Header
from pydantic import BaseModel
from apps.fincept_aiops.state_store import StateStore
from apps.fincept_aiops.audit_logger import AuditLogger

router = APIRouter(tags=["approval"])
state = StateStore()
audit = AuditLogger()


class ApprovalRequest(BaseModel):
    approved: bool
    approver_id: str
    reason: str = ""


@router.post("/approval/webhook")
def handle_approval(
    req: ApprovalRequest,
    x_approval_secret: str = Header(default=""),
):
    expected = os.getenv("APPROVAL_SECRET", "changeme")
    if x_approval_secret != expected:
        raise HTTPException(status_code=403, detail="invalid_secret")
    record = {
        "human_approved": req.approved,
        "approver_id": req.approver_id,
        "approved_at": datetime.utcnow().isoformat() + "Z",
        "reason": req.reason,
    }
    state.save("latest_approval", record)
    audit.append({
        "actor": req.approver_id,
        "action": "approval_decision",
        "approved": req.approved,
        "reason": req.reason,
    })
    return {"ok": True, "record": record}
