import logging
import threading
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class ProgressStep:
    name: str
    status: str = "waiting"  # waiting, running, completed, error
    message: str = ""
    count: int = 0


class ProgressTracker:
    """Real-time progress tracker bridging CrewAI execution to dashboard UI."""

    def __init__(self):
        self._steps: List[ProgressStep] = []
        self._current_step: int = -1
        self._lock = threading.Lock()
        self._callbacks: List[Callable] = []

    def reset(self):
        with self._lock:
            self._steps = [
                ProgressStep("Searching ArXiv"),
                ProgressStep("Searching Semantic Scholar"),
                ProgressStep("Searching Scopus"),
                ProgressStep("Searching CrossRef"),
                ProgressStep("Searching OpenAlex"),
                ProgressStep("Searching CORE"),
                ProgressStep("Searching PubMed"),
                ProgressStep("Searching DBLP"),
                ProgressStep("Searching Google Scholar"),
                ProgressStep("Searching IEEE Xplore"),
                ProgressStep("Searching ScienceDirect"),
                ProgressStep("Deduplicating papers"),
                ProgressStep("Ranking papers"),
                ProgressStep("Summarizing papers"),
                ProgressStep("Extracting limitations"),
                ProgressStep("Building citation graph"),
                ProgressStep("Finding best base paper"),
                ProgressStep("Finding top authors"),
                ProgressStep("Detecting research gaps"),
                ProgressStep("Generating problem statements"),
                ProgressStep("Generating ideas"),
            ]
            self._current_step = -1

    def on_step_start(self, step_name: str):
        with self._lock:
            for i, step in enumerate(self._steps):
                if step.name == step_name:
                    step.status = "running"
                    self._current_step = i
                    break
        self._notify()

    def on_step_complete(self, step_name: str, message: str = "", count: int = 0):
        with self._lock:
            for step in self._steps:
                if step.name == step_name:
                    step.status = "completed"
                    step.message = message
                    step.count = count
                    break
        self._notify()

    def on_step_error(self, step_name: str, error: str):
        with self._lock:
            for step in self._steps:
                if step.name == step_name:
                    step.status = "error"
                    step.message = error
                    break
        self._notify()

    def add_callback(self, callback: Callable):
        self._callbacks.append(callback)

    def _notify(self):
        for cb in self._callbacks:
            try:
                cb(self.get_progress())
            except Exception:
                pass

    def get_progress(self) -> Dict:
        with self._lock:
            total = len(self._steps)
            completed = sum(1 for s in self._steps if s.status == "completed")
            return {
                "steps": [
                    {"name": s.name, "status": s.status, "message": s.message, "count": s.count}
                    for s in self._steps
                ],
                "total": total,
                "completed": completed,
                "percent": int(completed / total * 100) if total > 0 else 0,
            }


progress_tracker = ProgressTracker()
