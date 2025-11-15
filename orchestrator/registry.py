import threading
from typing import Dict, Any


class AgentRegistry:
    """Thread-safe in-memory agent registry."""
    def __init__(self):
        self._lock = threading.Lock()
        self._agents: Dict[str, Dict[str, Any]] = {}

    def register(self, name: str, info: Dict[str, Any]):
        with self._lock:
            self._agents[name] = info

    def get(self, name: str):
        with self._lock:
            return self._agents.get(name)

    def all(self):
        with self._lock:
            return dict(self._agents)

    def clear(self):
        with self._lock:
            self._agents.clear()