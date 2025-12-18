import sys
import subprocess
import os
from pathlib import Path
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QLabel, QPushButton, QFrame,
                             QGridLayout, QMessageBox, QScrollArea)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QFont, QIcon, QPalette, QColor


class ProjectCard(QFrame):
    """Card représentant un projet"""

    def __init__(self, project_info, parent=None):
        super().__init__(parent)
        self.project_info = project_info
        self.init_ui()

    def init_ui(self):
        """Initialise l'interface de la card"""
        self.setFrameStyle(QFrame.Shape.Box)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: #34495e;
                border: 2px solid {self.project_info['color']};
                border-radius: 15px;
                padding: 5px;
            }}
        """)

        layout = QVBoxLayout()
        layout.setSpacing(15)

        # Icône et titre
        header_layout = QHBoxLayout()

        # Icône (emoji)
        icon_label = QLabel(self.project_info['icon'])
        icon_label.setStyleSheet("font-size: 48px; border: none; background-color: #2c3e50;")
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(icon_label)

        # Titre
        title = QLabel(self.project_info['name'])
        title.setStyleSheet(f"""
            font-size: 24px; 
            font-weight: bold; 
            color: {self.project_info['color']};
            background-color: #2c3e50;
            border: none;
        """)
        title.setWordWrap(True)
        header_layout.addWidget(title, 1)

        layout.addLayout(header_layout)

        # Description
        desc = QLabel(self.project_info['description'])
        desc.setStyleSheet("""
            font-size: 14px; 
            color: #ecf0f1;
            border: none;
            background-color: #2c3e50;
        """)
        desc.setWordWrap(True)
        desc.setMinimumHeight(55)
        desc.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        layout.addWidget(desc)

        # Séparateur
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setStyleSheet(f"background-color: {self.project_info['color']}; max-height: 2px; border: none;")
        layout.addWidget(line)

        # Bouton de lancement
        launch_btn = QPushButton(f"Lancer {self.project_info['name']}")
        launch_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.project_info['color']};
                color: white;
                border: none;
                padding: 15px;
                font-size: 16px;
                font-weight: bold;
                border-radius: 8px;
            }}
            QPushButton:hover {{
                background-color: {self.project_info['hover_color']};
            }}
            QPushButton:pressed {{
                background-color: {self.project_info['pressed_color']};
            }}
        """)
        launch_btn.clicked.connect(self.launch_project)
        layout.addWidget(launch_btn)

        layout.addStretch()
        self.setLayout(layout)

    def launch_project(self):
        """Lance le projet"""
        try:
            project_path = Path(self.project_info['path'])
            file_path = project_path / self.project_info['file']

            if not file_path.exists():
                QMessageBox.critical(
                    self,
                    "Erreur",
                    f"Le fichier {file_path} n'existe pas!\n\n"
                    f"Vérifiez que le chemin est correct:\n{file_path}"
                )
                return

            # Lancer le projet dans un nouveau processus
            if sys.platform == 'win32':
                subprocess.Popen([sys.executable, str(file_path)],
                               creationflags=subprocess.CREATE_NEW_CONSOLE)
            else:
                subprocess.Popen([sys.executable, str(file_path)])


        except Exception as e:
            QMessageBox.critical(
                self,
                "Erreur de Lancement",
                f"Impossible de lancer le projet:\n\n{str(e)}"
            )


class UnifiedLauncher(QMainWindow):
    """Fenêtre principale du lanceur unifié"""

    def __init__(self):
        super().__init__()
        self.projects = self.define_projects()
        self.init_ui()

    def define_projects(self):
        """Définit tous les projets"""
        return [
            {
                'name': 'Allocation de Processus',
                'description': 'Optimisation de l\'allocation de processus informatiques '
                              'avec contraintes de ressources, dépendances et incompatibilités. '
                              'Problème de sac à dos multidimensionnel.',
                'icon': '🖥️',
                'color': '#3498db',
                'hover_color': '#2980b9',
                'pressed_color': '#1f618d',
                'path': './projet1',
                'file': 'main.py'
            },
            {
                'name': 'Organisation des Visites Commerciales',
                'description': 'Optimisation des tournées des représentants commerciaux '
                               'pour desservir différents clients en respectant les '
                               'contraintes de temps, de compétences et de déplacements. '
                               'Problème de tournées de véhicules (VRP).',
                'icon': '🚚',
                'color': '#f39c12',
                'hover_color': '#d68910',
                'pressed_color': '#b9770e',
                'path': './projet2',
                'file': 'main.py'
            },
            {
                'name': 'Sélection de Canaux de Communication',
                'description': 'Optimisation de la sélection d’un ensemble maximal de canaux '
                               'de communication sans interférence. Modélisation par un '
                               'graphe de conflits et résolution du problème de stable set '
                               '(ensemble stable maximal).',
                'icon': '📡',
                'color': '#2ecc71',
                'hover_color': '#27ae60',
                'pressed_color': '#1e8449',
                'path': './projet3',
                'file': 'main.py'
            },
            {
                'name': 'Planification des Cours',
                'description': 'Optimisation de la planification des cours universitaires '
                               'afin de maximiser le nombre de cours programmés '
                               'simultanément sans conflit de salles, d’enseignants '
                               'ou d’horaires. Problème de graphe et d’ensemble stable.',
                'icon': '🎓',
                'color': '#e74c3c',
                'hover_color': '#c0392b',
                'pressed_color': '#a93226',
                'path': './projet4',
                'file': 'main.py'
            },
            {
                'name': 'Gestion des Stocks Énergétiques',
                'description': 'Optimisation de la production, du stockage et de '
                               'l’approvisionnement en carburant sur plusieurs périodes. '
                               'Application aux centrales énergétiques avec minimisation '
                               'des coûts totaux actualisés. Problème de planification '
                               'multi-périodes.',
                'icon': '⚡',
                'color': '#9b59b6',
                'hover_color': '#8e44ad',
                'pressed_color': '#76448a',
                'path': './projet5',
                'file': 'main.py'
            }
        ]

    def init_ui(self):
        """Initialise l'interface"""
        self.setWindowTitle("Recherche Opérationnelle - Lanceur de Projets")
        self.setGeometry(100, 100, 1400, 900)

        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(20)

        # Header
        header = self.create_header()
        main_layout.addWidget(header)

        # Zone de scroll pour les projets
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollBar:vertical {
                border: none;
                background: #1a1a1a;
                width: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background: #555;
                min-height: 20px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical:hover {
                background: #777;
            }
        """)

        # Conteneur des cards
        cards_widget = QWidget()
        cards_layout = QGridLayout(cards_widget)
        cards_layout.setSpacing(20)
        cards_layout.setContentsMargins(0, 0, 0, 0)

        # Créer les cards (2 par ligne)
        for i, project in enumerate(self.projects):
            card = ProjectCard(project)
            row = i // 2
            col = i % 2
            cards_layout.addWidget(card, row, col)

        scroll.setWidget(cards_widget)
        main_layout.addWidget(scroll)

    def create_header(self):
        """Crée l'en-tête"""
        header = QFrame()
        header.setStyleSheet("""
            QFrame {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #2c3e50,
                    stop:1 #3498db
                );
                border-radius: 15px;
                padding: 5px;
            }
        """)

        layout = QVBoxLayout(header)

        # Titre principal
        title = QLabel("Projets de Recherche Opérationnelle")
        title.setStyleSheet("""
            font-size: 36px;
            font-weight: bold;
            color: white;
            border: none;
        """)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        return header

def main():
    """Fonction principale"""
    app = QApplication(sys.argv)

    # Style global
    app.setStyle('Fusion')

    # Palette sombre
    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor(26, 26, 26))
    palette.setColor(QPalette.ColorRole.WindowText, QColor(255, 255, 255))
    palette.setColor(QPalette.ColorRole.Base, QColor(35, 35, 35))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor(44, 44, 44))
    palette.setColor(QPalette.ColorRole.Text, QColor(255, 255, 255))
    palette.setColor(QPalette.ColorRole.Button, QColor(53, 53, 53))
    palette.setColor(QPalette.ColorRole.ButtonText, QColor(255, 255, 255))
    app.setPalette(palette)

    # Lancer la fenêtre
    window = UnifiedLauncher()
    window.show()

    sys.exit(app.exec())


if __name__ == '__main__':
    main()