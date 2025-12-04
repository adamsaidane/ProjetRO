from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QLabel, QCheckBox,
                             QScrollArea, QWidget, QDialogButtonBox)


class DependencyDialog(QDialog):
    def __init__(self, process_name, all_processes, current_dependencies, parent=None):
        super().__init__(parent)
        self.process_name = process_name
        self.all_processes = all_processes
        self.selected_dependencies = current_dependencies.copy()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle(f"Dépendances de {self.process_name}")
        self.setMinimumWidth(400)

        layout = QVBoxLayout()

        # Description
        label = QLabel(f"Sélectionnez les processus dont '{self.process_name}' dépend:")
        label.setWordWrap(True)
        layout.addWidget(label)

        # Liste des processus disponibles
        self.checkboxes = {}
        scroll = QScrollArea()
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)

        for proc in self.all_processes:
            if proc.name != self.process_name:  # Ne pas inclure le processus lui-même
                checkbox = QCheckBox(f"{proc.name} (Priorité: {proc.priority})")
                checkbox.setChecked(proc.name in self.selected_dependencies)
                self.checkboxes[proc.name] = checkbox
                scroll_layout.addWidget(checkbox)

        scroll_layout.addStretch()
        scroll.setWidget(scroll_widget)
        scroll.setWidgetResizable(True)
        layout.addWidget(scroll)

        # Boutons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

        self.setLayout(layout)

    def get_selected_dependencies(self):
        dependencies = []
        for name, checkbox in self.checkboxes.items():
            if checkbox.isChecked():
                dependencies.append(name)
        return dependencies