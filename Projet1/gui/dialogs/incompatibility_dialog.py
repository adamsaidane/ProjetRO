from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QLabel, QCheckBox,
                             QScrollArea, QWidget, QDialogButtonBox)


class IncompatibilityDialog(QDialog):
    def __init__(self, process_name, all_processes, current_incompatibilities, parent=None):
        super().__init__(parent)
        self.process_name = process_name
        self.all_processes = all_processes
        self.selected_incompatibilities = current_incompatibilities.copy()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle(f"Incompatibilités de {self.process_name}")
        self.setMinimumWidth(400)

        layout = QVBoxLayout()

        # Description
        label = QLabel(f"Sélectionnez les processus incompatibles avec '{self.process_name}':")
        label.setWordWrap(True)
        layout.addWidget(label)

        # Liste des processus disponibles
        self.checkboxes = {}
        scroll = QScrollArea()
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)

        for proc in self.all_processes:
            if proc.name != self.process_name:
                checkbox = QCheckBox(f"{proc.name} (Priorité: {proc.priority})")
                checkbox.setChecked(proc.name in self.selected_incompatibilities)
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

    def get_selected_incompatibilities(self):
        incompatibilities = []
        for name, checkbox in self.checkboxes.items():
            if checkbox.isChecked():
                incompatibilities.append(name)
        return incompatibilities