import json
import os
from datetime import datetime
from pathlib import Path


class AuditLogger:
    def __init__(self, path: str = None):
        self.path = Path(path or os.getenv("AUDIT_LOG_PATH", "./data/audit/audit.jsonl"))
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def append(self, record: dict):
        record.setdefault("ts", datetime.utcnow().isoformat() + "Z")
        with open(self.path, "a", encoding="utf-8") as f:
            f.write(json.dumps(record) + "\n")

    def recent(self, n: int = 50):
        if not self.path.exists():
            return []
        lines = self.path.read_text(encoding="utf-8").strip().split("\n")
        return [json.loads(l) for l in lines[-n:] if l]
