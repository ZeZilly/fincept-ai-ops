from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Dict, Any
from apps.fincept_aiops.paper_broker import PaperBrokerAdapter
from apps.fincept_aiops.risk_policy import RiskPolicy
from apps.fincept_aiops.audit_logger import AuditLogger

router = APIRouter(tags=["broker"])
broker = PaperBrokerAdapter()
risk = RiskPolicy()
audit = AuditLogger()


class PaperOrderRequest(BaseModel):
    order_intent: Dict[str, Any]
    portfolio_context: Dict[str, Any] = Field(default_factory=dict)
    human_approved: bool = False


class ClosePositionRequest(BaseModel):
    asset: str
    price: float


@router.post("/broker/paper-submit")
def paper_submit(req: PaperOrderRequest):
    decision = risk.evaluate(req.order_intent, req.portfolio_context)
    if decision["status"] != "approved" or not req.human_approved:
        audit.append({"actor": "execution_ops", "action": "blocked_paper_submit",
                      "asset": req.order_intent.get("asset"), "risk_status": decision["status"],
                      "human_approved": req.human_approved})
        raise HTTPException(status_code=403, detail={"ok": False, "risk_decision": decision, "human_approved": req.human_approved})
    result = broker.submit_order(req.order_intent)
    audit.append({"actor": "execution_ops", "action": "submit_paper_order",
                  "asset": req.order_intent.get("asset"), "side": req.order_intent.get("side"),
                  "status": "filled", "order_id": result["order"]["order_id"]})
    return {"ok": True, "result": result, "risk_decision": decision}


@router.post("/broker/close-position")
def close_position(req: ClosePositionRequest):
    result = broker.close_position(req.asset, req.price)
    if not result["ok"]:
        raise HTTPException(status_code=400, detail=result)
    audit.append({"actor": "execution_ops", "action": "close_position",
                  "asset": req.asset.upper(), "realized_pnl": result["realized_pnl"]})
    return result


@router.get("/broker/reconcile")
def reconcile():
    return {"positions": broker.get_positions(), "orders": broker.get_orders(), "summary": broker.get_summary()}
