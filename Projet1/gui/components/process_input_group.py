from PyQt6.QtWidgets import QGroupBox, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QSpinBox, QDoubleSpinBox, QPushButton

class ProcessInputGroup(QGroupBox):
    def __init__(self, parent):
        super().__init__("Ajouter un Processus")
        self.parent = parent
        process_layout = QVBoxLayout(self)

        # Nom
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("Nom:"))
        self.parent.name_input = QComboBox()
        self.parent.name_input.setEditable(True)
        self.parent.name_input.addItems(["WebServer", "Database", "Cache", "Analytics",
                                         "Backup", "Monitoring", "Logging", "TestEnv"])
        name_layout.addWidget(self.parent.name_input)
        process_layout.addLayout(name_layout)

        # Valeur
        value_layout = QHBoxLayout()
        value_layout.addWidget(QLabel("Valeur:"))
        self.parent.value_spin = QSpinBox()
        self.parent.value_spin.setRange(1, 10000)
        self.parent.value_spin.setValue(100)
        value_layout.addWidget(self.parent.value_spin)
        process_layout.addLayout(value_layout)

        # CPU
        cpu_proc_layout = QHBoxLayout()
        cpu_proc_layout.addWidget(QLabel("CPU (%):"))
        self.parent.cpu_proc_spin = QDoubleSpinBox()
        self.parent.cpu_proc_spin.setRange(0.1, 100)
        self.parent.cpu_proc_spin.setValue(10.0)
        cpu_proc_layout.addWidget(self.parent.cpu_proc_spin)
        process_layout.addLayout(cpu_proc_layout)

        # RAM
        ram_proc_layout = QHBoxLayout()
        ram_proc_layout.addWidget(QLabel("RAM (GB):"))
        self.parent.ram_proc_spin = QDoubleSpinBox()
        self.parent.ram_proc_spin.setRange(0.1, 100)
        self.parent.ram_proc_spin.setValue(2.0)
        ram_proc_layout.addWidget(self.parent.ram_proc_spin)
        process_layout.addLayout(ram_proc_layout)

        # Threads
        threads_proc_layout = QHBoxLayout()
        threads_proc_layout.addWidget(QLabel("Threads:"))
        self.parent.threads_proc_spin = QSpinBox()
        self.parent.threads_proc_spin.setRange(1, 100)
        self.parent.threads_proc_spin.setValue(4)
        threads_proc_layout.addWidget(self.parent.threads_proc_spin)
        process_layout.addLayout(threads_proc_layout)

        # Priorité
        priority_proc_layout = QHBoxLayout()
        priority_proc_layout.addWidget(QLabel("Priorité:"))
        self.parent.priority_combo = QComboBox()
        self.parent.priority_combo.addItems(["Critique (1)", "Haute (2)", "Normale (3)", "Basse (4)"])
        self.parent.priority_combo.setCurrentIndex(2)
        priority_proc_layout.addWidget(self.parent.priority_combo)
        process_layout.addLayout(priority_proc_layout)

        # Durée
        duration_layout = QHBoxLayout()
        duration_layout.addWidget(QLabel("Durée (s):"))
        self.parent.duration_spin = QSpinBox()
        self.parent.duration_spin.setRange(0, 999999)
        self.parent.duration_spin.setValue(3600)
        duration_layout.addWidget(self.parent.duration_spin)
        process_layout.addLayout(duration_layout)

        # Boutons
        btn_layout = QHBoxLayout()
        add_btn = QPushButton("Ajouter")
        add_btn.clicked.connect(self.parent.add_process)
        add_btn.setStyleSheet("background-color: #2ecc71; color: white; padding: 5px; font-weight: bold;")
        btn_layout.addWidget(add_btn)

        clear_btn = QPushButton("Effacer Tout")
        clear_btn.clicked.connect(self.parent.clear_all)
        clear_btn.setStyleSheet("background-color: #e74c3c; color: white; padding: 5px; font-weight: bold;")
        btn_layout.addWidget(clear_btn)
        process_layout.addLayout(btn_layout)