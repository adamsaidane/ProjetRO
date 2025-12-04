from PyQt6.QtCore import QThread, pyqtSignal
from Projet1.core.optimizer import ProcessAllocationOptimizer


class OptimizationThread(QThread):
    """Thread pour exécuter l'optimisation sans bloquer l'interface"""
    finished = pyqtSignal(object)  # Émet OptimizationResult
    error = pyqtSignal(str)

    def __init__(self, processes, config):
        super().__init__()
        self.processes = processes
        self.config = config

    def run(self):
        try:
            optimizer = ProcessAllocationOptimizer()
            results = optimizer.solve(self.processes, self.config)
            self.finished.emit(results)
        except Exception as e:
            self.error.emit(f"Erreur lors de l'optimisation: {str(e)}")