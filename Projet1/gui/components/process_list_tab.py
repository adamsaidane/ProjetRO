from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTableWidget

class ProcessListTab(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        layout = QVBoxLayout(self)

        self.process_table = QTableWidget()
        self.process_table.verticalHeader().setDefaultSectionSize(48)
        self.process_table.setAlternatingRowColors(True)
        self.process_table.setStyleSheet("""
            QTableWidget {
                alternate-background-color: #28231D;
            }
        """)
        self.process_table.verticalHeader().setVisible(False)
        self.process_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.process_table.setShowGrid(False)
        self.process_table.setColumnCount(10)
        self.process_table.setHorizontalHeaderLabels([
            "Nom", "Valeur", "CPU (%)", "RAM (GB)", "Threads",
            "Priorité", "Durée (s)", "Dépendances", "Incompatibilités", "Actions"
        ])
        self.process_table.horizontalHeader().setStretchLastSection(True)

        # Ajuster la largeur des colonnes
        self.process_table.setColumnWidth(0, 100)  # Nom
        self.process_table.setColumnWidth(7, 120)  # Dépendances
        self.process_table.setColumnWidth(8, 120)  # Incompatibilités

        layout.addWidget(self.process_table)