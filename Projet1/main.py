import sys
from PyQt6.QtWidgets import QApplication
from gui.main_window import ProcessAllocationGUI
from utils.styles import APP_STYLESHEET


def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    app.setStyleSheet(APP_STYLESHEET)

    window = ProcessAllocationGUI()
    window.show()

    sys.exit(app.exec())


if __name__ == '__main__':
    main()