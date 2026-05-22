import json
import os
from pathlib import Path
from typing import Any


class StateStore:
    def __init__(self, base: str = None):
        self.base = Path(base or os.getenv("STATE_PATH", "./data/state"))
        self.base.mkdir(parents=True, exist_ok=True)

    def save(self, key: str, data: Any):
        (self.base / f"{key}.json").write_text(
            json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8"
        )

    def load(self, key: str) -> Any:
        p = self.base / f"{key}.json"
        return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None

    def exists(self, key: str) -> bool:
        return (self.base / f"{key}.json").exists()
