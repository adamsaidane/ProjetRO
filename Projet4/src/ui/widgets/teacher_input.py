from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QHeaderView, QLineEdit, QLabel
)
from PyQt6.QtCore import Qt
from typing import List, Set
from ...models.teacher import Teacher

class TeacherInputWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()

        # Instructions
        layout.addWidget(QLabel("Add teachers and the subjects they can teach:"))

        # Table
        self.table = QTableWidget(0, 2)
        self.table.setHorizontalHeaderLabels(["Teacher Name", "Subjects (comma-separated)"])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.table)

        # Buttons
        btn_layout = QHBoxLayout()
        self.add_btn = QPushButton("➕ Add Teacher")
        self.add_btn.clicked.connect(self.add_row)
        self.remove_btn = QPushButton("🗑️ Remove Selected")
        self.remove_btn.clicked.connect(self.remove_selected)
        btn_layout.addWidget(self.add_btn)
        btn_layout.addWidget(self.remove_btn)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)

        self.setLayout(layout)
        self.add_row()  # start with one row

    def add_row(self):
        row = self.table.rowCount()
        self.table.insertRow(row)
        self.table.setItem(row, 0, QTableWidgetItem(""))
        self.table.setItem(row, 1, QTableWidgetItem(""))

    def remove_selected(self):
        rows = sorted(set(i.row() for i in self.table.selectedItems()), reverse=True)
        for row in rows:
            self.table.removeRow(row)

    def get_teachers(self) -> List[Teacher]:
        teachers = []
        for row in range(self.table.rowCount()):
            name_item = self.table.item(row, 0)
            subs_item = self.table.item(row, 1)
            if not name_item or not subs_item:
                continue
            name = name_item.text().strip()
            if not name:
                continue
            subjects = {s.strip() for s in subs_item.text().split(",") if s.strip()}
            if subjects:
                teachers.append(Teacher(name, subjects))
        return teachers