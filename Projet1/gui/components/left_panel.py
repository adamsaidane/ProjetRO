from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton

from Projet1.gui.components.system_config_group import SystemConfigGroup
from Projet1.gui.components.priority_constraints_group import PriorityConstraintsGroup
from Projet1.gui.components.process_input_group import ProcessInputGroup

class LeftPanel(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        left_layout = QVBoxLayout(self)
        left_layout.setContentsMargins(10, 10, 10, 10)
        left_layout.setSpacing(12)

        # Groupes extraits
        config_group = SystemConfigGroup(parent)
        left_layout.addWidget(config_group)

        priority_group = PriorityConstraintsGroup(parent)
        left_layout.addWidget(priority_group)

        process_group = ProcessInputGroup(parent)
        left_layout.addWidget(process_group)

        # Bouton charger exemple
        load_example_btn = QPushButton("Charger Données Exemple")
        load_example_btn.clicked.connect(self.parent.load_example_data)
        load_example_btn.setStyleSheet("""
            background-color: #3498db; 
            color: white; 
            padding: 8px;
            font-weight: bold;
            border-radius: 4px;
        """)
        left_layout.addWidget(load_example_btn)

        left_layout.addStretch()