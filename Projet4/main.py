import sys
import os
from PyQt6.QtWidgets import QApplication
from src.ui.main_window import MainWindow

def main():
    # Optional: set high-DPI scaling
    os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "1"
    
    app = QApplication(sys.argv)
    app.setStyle("Fusion")  # consistent cross-platform look
    
    # Optional: load stylesheet
    # with open("resources/style.qss") as f:
    #     app.setStyleSheet(f.read())

    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()