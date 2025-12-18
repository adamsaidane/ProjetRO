from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot
import traceback
from typing import List, Dict
import networkx as nx
from ..models.lesson import Lesson
from .solver import solve_mwis_gurobi

class SolverWorker(QObject):
    """
    Worker object to run Gurobi optimization in a background thread.
    Communicates with UI via signals (thread-safe).
    """
    # Signals (emitted from worker thread → received in UI thread)
    started = pyqtSignal()
    finished = pyqtSignal(list)        # List[Lesson]
    failed = pyqtSignal(str)           # error message
    progress = pyqtSignal(str)         # status message (optional)

    def __init__(self):
        super().__init__()
        self._G = None
        self._lessons = []
        self._weights = None
        self._is_cancelled = False

    @pyqtSlot(nx.Graph, list, dict)
    def set_data(self, G: nx.Graph, lessons: List[Lesson], weights: Dict[Lesson, float] = None):
        """Set data for next solve (called from UI thread before starting)."""
        self._G = G
        self._lessons = lessons
        self._weights = weights
        self._is_cancelled = False

    @pyqtSlot()
    def solve(self):
        """
        Run optimization. Called via moveToThread + start().
        Emits finished/failed signals.
        """
        try:
            self.started.emit()
            self.progress.emit("🔍 Building model...")

            if self._is_cancelled:
                return

            # 🔥 This is the heavy part — runs in background thread
            result = solve_mwis_gurobi(self._G, self._lessons, self._weights)

            if self._is_cancelled:
                return

            self.finished.emit(result)

        except Exception as e:
            # Capture full traceback for debugging
            error_msg = f"{type(e).__name__}: {str(e)}\n\n{traceback.format_exc()}"
            self.failed.emit(error_msg)

    @pyqtSlot()
    def cancel(self):
        """Request cancellation (Gurobi also supports callbacks for true abort)."""
        self._is_cancelled = True