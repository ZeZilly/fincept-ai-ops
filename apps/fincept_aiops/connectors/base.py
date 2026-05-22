from abc import ABC, abstractmethod
from typing import Any, Dict


class BaseConnector(ABC):
    name: str = "base"

    @abstractmethod
    def fetch(self, params: Dict[str, Any]) -> Dict[str, Any]: ...

    def health(self) -> Dict[str, Any]:
        return {"connector": self.name, "status": "ok"}
