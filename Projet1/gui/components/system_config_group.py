from PyQt6.QtWidgets import QGroupBox, QVBoxLayout, QHBoxLayout, QLabel, QSpinBox, QDoubleSpinBox

class SystemConfigGroup(QGroupBox):
    def __init__(self, parent):
        super().__init__("Configuration du Système")
        self.parent = parent
        config_layout = QVBoxLayout(self)

        # CPU Max
        cpu_layout = QHBoxLayout()
        cpu_layout.addWidget(QLabel("CPU Max (%):"))
        self.parent.cpu_max_spin = QSpinBox()
        self.parent.cpu_max_spin.setRange(1, 100)
        self.parent.cpu_max_spin.setValue(100)
        cpu_layout.addWidget(self.parent.cpu_max_spin)
        config_layout.addLayout(cpu_layout)

        # RAM Max
        ram_layout = QHBoxLayout()
        ram_layout.addWidget(QLabel("RAM Max (GB):"))
        self.parent.ram_max_spin = QDoubleSpinBox()
        self.parent.ram_max_spin.setRange(0.1, 1024)
        self.parent.ram_max_spin.setValue(16.0)
        self.parent.ram_max_spin.setDecimals(1)
        ram_layout.addWidget(self.parent.ram_max_spin)
        config_layout.addLayout(ram_layout)

        # Threads Max
        threads_layout = QHBoxLayout()
        threads_layout.addWidget(QLabel("Threads Max:"))
        self.parent.threads_max_spin = QSpinBox()
        self.parent.threads_max_spin.setRange(1, 1000)
        self.parent.threads_max_spin.setValue(32)
        threads_layout.addWidget(self.parent.threads_max_spin)
        config_layout.addLayout(threads_layout)

        # Temps Max
        time_layout = QHBoxLayout()
        time_layout.addWidget(QLabel("Temps Max (s):"))
        self.parent.time_max_spin = QSpinBox()
        self.parent.time_max_spin.setRange(0, 999999)
        self.parent.time_max_spin.setValue(0)
        self.parent.time_max_spin.setSpecialValueText("Illimité")
        time_layout.addWidget(self.parent.time_max_spin)
        config_layout.addLayout(time_layout)