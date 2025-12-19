import sys
from PyQt6.QtWidgets import QApplication

from .infrastructure.gurobi_solver import GurobiTelecomSolver
from .application.use_cases import TelecomUseCase
from .presentation.window import TelecomWindow

def main():
    app = QApplication(sys.argv)

    solver = GurobiTelecomSolver()
    use_case = TelecomUseCase(solver)
    win = TelecomWindow(use_case)
    win.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
