"""
Projet RO - Ordonnancement Multi-Période
Gestion des stocks de carburant pour centrales électriques
Point d'entrée de l'application
"""

import sys
from PySide6.QtWidgets import QApplication
from interface import MainWindow

def main():
    """Point d'entrée principal de l'application"""
    app = QApplication(sys.argv)
    app.setStyle('Fusion')  # Style moderne
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())

if __name__ == '__main__':
    main()