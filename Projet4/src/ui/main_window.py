from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QTabWidget, QMessageBox
)
from .widgets.teacher_input import TeacherInputWidget
from .widgets.class_input import ClassInputWidget
from .widgets.result_display import ResultDisplayWidget

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🏫 School Timetabling Assistant")
        self.resize(900, 700)

        # Central widget
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        # Tabs
        self.tabs = QTabWidget()
        self.teacher_widget = TeacherInputWidget()
        self.class_widget = ClassInputWidget()
        self.result_widget = ResultDisplayWidget()

        self.tabs.addTab(self.teacher_widget, "🧑‍🏫 Teachers")
        self.tabs.addTab(self.class_widget, "🎓 Classes")
        self.tabs.addTab(self.result_widget, "✅ Schedule")

        layout.addWidget(self.tabs)

        # Compute button
        self.compute_btn = QPushButton("🚀 Compute Optimal Simultaneous Lessons")
        self.compute_btn.clicked.connect(self.on_compute)
        self.compute_btn.setStyleSheet("font-size: 14px; padding: 8px;")
        layout.addWidget(self.compute_btn)

    def on_compute(self):
        try:
            teachers = self.teacher_widget.get_teachers()
            classes = self.class_widget.get_classes()

            if not teachers:
                raise ValueError("No valid teachers provided.")
            if not classes:
                raise ValueError("No valid classes provided.")

            self.result_widget.update_results(teachers, classes)
            self.tabs.setCurrentIndex(2)  # switch to results

        except Exception as e:
            QMessageBox.warning(self, "Input Error", f"Invalid input:\n{str(e)}")