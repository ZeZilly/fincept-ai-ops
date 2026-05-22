from typing import Any, Dict
from apps.fincept_aiops.connectors.base import BaseConnector
from apps.fincept_aiops.paper_broker import PaperBrokerAdapter


class BrokerSandboxConnector(BaseConnector):
    name = "broker_sandbox"

    def __init__(self):
        self.broker = PaperBrokerAdapter()

    def fetch(self, params: Dict[str, Any]) -> Dict[str, Any]:
        action = params.get("action", "submit")
        if action == "submit":
            return self.broker.submit_order(params.get("order_intent", {}))
        if action == "close":
            return self.broker.close_position(params.get("asset", ""), float(params.get("price", 0)))
        if action == "reconcile":
            return {"positions": self.broker.get_positions(), "orders": self.broker.get_orders(), "summary": self.broker.get_summary()}
        return {"ok": False, "error": f"unknown_action: {action}"}
