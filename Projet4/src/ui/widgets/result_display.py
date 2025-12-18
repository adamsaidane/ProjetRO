from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QLabel, QPushButton,
    QHBoxLayout, QMessageBox
)
from PyQt6.QtCore import Qt
from ...models.lesson import Lesson
from ...visualization.interactive_plot import visualize_conflict_graph_interactive
from ...visualization.static_plot import visualize_with_solution
import networkx as nx
from ...core.conflict_graph import build_conflict_graph
from ...core.lesson_generator import generate_lessons
from PyQt6.QtCore import QThread
from ...core.solver_worker import SolverWorker
from .progress_dialog import ProgressDialog

class ResultDisplayWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.lessons = []
        self.G = None
        self.setup_ui()
        self.setup_worker()

    def setup_worker(self):
        # Create worker and thread
        self.thread = QThread()
        self.worker = SolverWorker()
        self.worker.moveToThread(self.thread)

        # Connect signals
        self.worker.started.connect(self.on_solver_started)
        self.worker.finished.connect(self.on_solver_finished)
        self.worker.failed.connect(self.on_solver_failed)
        self.worker.progress.connect(self.on_solver_progress)

        # Start thread (but worker idle until solve() called)
        self.thread.start()
        
    def setup_ui(self):
        layout = QVBoxLayout()

        self.title = QLabel("⏳ No schedule computed yet.")
        self.title.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(self.title)

        # Table
        self.table = QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(["Class", "Subject", "Teacher"])
        self.table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.table)

        # Buttons
        btn_layout = QHBoxLayout()
        self.plot_btn = QPushButton("📊 Show Conflict Graph")
        self.plot_btn.clicked.connect(self.show_graph)
        self.plot_btn.setEnabled(False)

        self.html_btn = QPushButton("🌐 Open Interactive Graph")
        self.html_btn.clicked.connect(self.open_interactive)
        self.html_btn.setEnabled(False)

        btn_layout.addWidget(self.plot_btn)
        btn_layout.addWidget(self.html_btn)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)

        self.setLayout(layout)

    def update_results(self, teachers, classes):
        """Initiate async solve."""
        try:
            self.lessons = generate_lessons(teachers, classes)
            if not self.lessons:
                raise ValueError("No feasible lessons found.")

            self.G = build_conflict_graph(self.lessons)

            # Show progress dialog
            self.progress_dialog = ProgressDialog(self)
            self.progress_dialog.cancelled.connect(self.cancel_solver)
            self.progress_dialog.open()

            # Configure worker & start
            self.worker.set_data(self.G, self.lessons)
            self.thread.start()  # ensure thread is running
            self.worker.solve()  # this calls solve() in worker thread

        except Exception as e:
            QMessageBox.critical(self, "Setup Error", f"Failed to prepare input:\n{str(e)}")
            if hasattr(self, 'progress_dialog') and self.progress_dialog.isVisible():
                self.progress_dialog.close()

    # Slot: called when solver starts
    def on_solver_started(self):
        if hasattr(self, 'progress_dialog') and self.progress_dialog.isVisible():
            self.progress_dialog.set_message("🚀 Solving with Gurobi...")

    # Slot: called on progress update (optional)
    def on_solver_progress(self, msg: str):
        if hasattr(self, 'progress_dialog') and self.progress_dialog.isVisible():
            self.progress_dialog.set_message(msg)

    # Slot: called on success
    def on_solver_finished(self, solution: list[Lesson]):
        if hasattr(self, 'progress_dialog'):
            self.progress_dialog.close()

        self.solution = solution
        self.title.setText(f"✅ Optimal schedule: {len(self.solution)} lessons can run simultaneously")
        self.table.setRowCount(len(self.solution))
        for i, lesson in enumerate(self.solution):
            self.table.setItem(i, 0, QTableWidgetItem(lesson.class_name))
            self.table.setItem(i, 1, QTableWidgetItem(lesson.subject))
            self.table.setItem(i, 2, QTableWidgetItem(lesson.teacher_name))

        self.plot_btn.setEnabled(True)
        self.html_btn.setEnabled(True)

    # Slot: called on error
    def on_solver_failed(self, error_msg: str):
        if hasattr(self, 'progress_dialog'):
            self.progress_dialog.close()

        QMessageBox.critical(self, "Optimization Failed", f"Solver error:\n{error_msg}")
        self.title.setText("❌ Optimization failed")
        self.table.setRowCount(0)
        self.plot_btn.setEnabled(False)
        self.html_btn.setEnabled(False)

    # Slot: cancel button pressed
    def cancel_solver(self):
        if self.worker:
            self.worker.cancel()
        if hasattr(self, 'thread') and self.thread.isRunning():
            # Note: Gurobi doesn’t support true async abort via Python API easily,
            # but setting _is_cancelled prevents post-solve processing.
            pass
    def show_graph(self):
        if not self.lessons:
            return
        G = build_conflict_graph(self.lessons)
        visualize_with_solution(G, self.lessons, self.solution)

    def open_interactive(self):
        if not self.lessons:
            return
        G = build_conflict_graph(self.lessons)
        visualize_conflict_graph_interactive(G, self.lessons, "schedule_conflicts.html")
    def closeEvent(self, event):
        # Graceful shutdown
        if hasattr(self, 'thread') and self.thread.isRunning():
            self.thread.quit()
            self.thread.wait(2000)  # 2 sec timeout
        super().closeEvent(event)