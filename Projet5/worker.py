"""
Worker thread pour l'optimisation non-bloquante
Utilise QThread pour éviter de bloquer l'interface
"""

from PySide6.QtCore import QThread, Signal
from model import FuelManagementModel

class OptimizationWorker(QThread):
    """Thread pour exécuter l'optimisation sans bloquer l'UI"""
    
    finished = Signal(dict)
    error = Signal(str)
    
    def __init__(self, data):
        super().__init__()
        self.data = data
        self.model = None
    
    def run(self):
        """Exécute l'optimisation"""
        try:
            # Créer le modèle
            self.model = FuelManagementModel()
            
            # Construire le modèle
            self.model.build_model(self.data)
            
            # Optimiser
            success = self.model.optimize()
            
            if success:
                # Extraire les résultats
                results = self.model.get_results()
                self.finished.emit(results)
            else:
                self.error.emit("Le solveur n'a pas trouvé de solution optimale")
                
        except Exception as e:
            self.error.emit(str(e))