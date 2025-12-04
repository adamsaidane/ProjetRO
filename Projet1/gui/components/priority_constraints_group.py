from PyQt6.QtWidgets import QGroupBox, QVBoxLayout, QHBoxLayout, QLabel, QSpinBox

class PriorityConstraintsGroup(QGroupBox):
    def __init__(self, parent):
        super().__init__("Contraintes de Priorité")
        self.parent = parent
        priority_layout = QVBoxLayout(self)

        # Min critiques
        min_crit_layout = QHBoxLayout()
        min_crit_layout.addWidget(QLabel("Min Critiques:"))
        self.parent.min_critical_spin = QSpinBox()
        self.parent.min_critical_spin.setRange(0, 100)
        self.parent.min_critical_spin.setValue(0)
        min_crit_layout.addWidget(self.parent.min_critical_spin)
        priority_layout.addLayout(min_crit_layout)

        # Max basse priorité
        max_low_layout = QHBoxLayout()
        max_low_layout.addWidget(QLabel("Max Basse Priorité:"))
        self.parent.max_low_spin = QSpinBox()
        self.parent.max_low_spin.setRange(0, 100)
        self.parent.max_low_spin.setValue(0)
        self.parent.max_low_spin.setSpecialValueText("Illimité")
        max_low_layout.addWidget(self.parent.max_low_spin)
        priority_layout.addLayout(max_low_layout)