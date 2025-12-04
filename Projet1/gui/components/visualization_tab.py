from PyQt6.QtWidgets import QWidget, QVBoxLayout
from Projet1.gui.widgets.matplotlib_widget import MatplotlibWidget

class VisualizationTab(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        layout = QVBoxLayout(self)

        self.matplotlib_widget = MatplotlibWidget()
        layout.addWidget(self.matplotlib_widget)