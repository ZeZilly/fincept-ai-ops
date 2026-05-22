from apps.fincept_aiops.audit_logger import AuditLogger
from typing import Any, Dict


class AuditAgent:
    """Agent 6 — append-only audit trail."""
    def __init__(self):
        self.logger = AuditLogger()
    def log(self, record: Dict[str, Any]):
        self.logger.append(record)
    def recent(self, n: int = 50):
        return self.logger.recent(n)
