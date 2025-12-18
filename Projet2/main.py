import sys
import os
from PyQt5.QtWidgets import QApplication
from gui import MainWindow


def main():
    """Main application entry point"""
    app = QApplication(sys.argv)
    app.setStyle('Fusion')  # Modern style

    # Set application icon and name
    app.setApplicationName("Sales Routing Optimizer - Multiple Vehicles")

    window = MainWindow()
    window.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()