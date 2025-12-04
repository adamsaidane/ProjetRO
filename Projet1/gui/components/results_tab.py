from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout, QFrame, QScrollArea
from PyQt6.QtCore import Qt


class ResultsTab(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(14)

        # --- TITRE ---
        title = QLabel("Dashboard d'Optimisation")
        title.setStyleSheet("font-size: 22px; font-weight: bold; color: white; padding-bottom: 5px;")
        layout.addWidget(title)

        # Résumé synthétique (KPI)
        kpi_row = QWidget()
        kpi_layout = QHBoxLayout(kpi_row)
        kpi_layout.setContentsMargins(0, 0, 0, 0)
        kpi_layout.setSpacing(12)

        self.kpi_cpu_card, self.kpi_cpu = self.make_kpi_widget("🖥️", "Charge CPU", "#3498db")
        self.kpi_ram_card, self.kpi_ram = self.make_kpi_widget("💾", "Usage RAM", "#2ecc71")
        self.kpi_threads_card, self.kpi_threads = self.make_kpi_widget("🧵", "Total Threads", "#f1c40f")
        self.kpi_value_card, self.kpi_value = self.make_kpi_widget("⭐", "Valeur Totale", "#9b59b6")

        kpi_layout.addWidget(self.kpi_cpu_card)
        kpi_layout.addWidget(self.kpi_ram_card)
        kpi_layout.addWidget(self.kpi_threads_card)
        kpi_layout.addWidget(self.kpi_value_card)

        layout.addWidget(kpi_row)

        # Résumé texte
        self.results_summary = QLabel("En attente d'optimisation...")
        self.results_summary.setStyleSheet("font-size:12px; color:#aaa; font-style: italic; padding: 5px;")
        layout.addWidget(self.results_summary)

        # Séparateur visuel
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setStyleSheet("background-color: #333; max-height: 1px;")
        layout.addWidget(line)

        # --- CONTENEUR DES CARDS DE PROCESSUS ---
        self.process_cards_container = QWidget()
        self.process_cards_container.setStyleSheet("background-color: transparent;")
        self.process_cards_layout = QVBoxLayout(self.process_cards_container)
        self.process_cards_layout.setSpacing(12)
        self.process_cards_layout.setContentsMargins(0, 5, 0, 5)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(self.process_cards_container)
        scroll.setStyleSheet("""
            QScrollArea { border: none; background-color: transparent; }
            QScrollBar:vertical {
                border: none;
                background: #121212;
                width: 10px;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical {
                background: #333;
                min-height: 20px;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical:hover { background: #444; }
        """)
        layout.addWidget(scroll)

    def make_kpi_widget(self, icon, label_text, color_accent):
        card = QFrame()
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(12, 12, 12, 12)
        card_layout.setSpacing(4)

        icon_lbl = QLabel(icon)
        icon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_lbl.setStyleSheet(f"font-size:20px; color: {color_accent};")

        label = QLabel(label_text.upper())
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setStyleSheet("font-size:10px; font-weight: bold; color:#888;")

        value = QLabel("--")
        value.setAlignment(Qt.AlignmentFlag.AlignCenter)
        value.setStyleSheet(f"font-size:18px; font-weight:bold; color: {color_accent};")

        card_layout.addWidget(icon_lbl)
        card_layout.addWidget(label)
        card_layout.addWidget(value)

        card.setStyleSheet(f"""
            QFrame {{
                background-color: #1e1e1e;
                border: 1px solid #333;
                border-bottom: 3px solid {color_accent};
                border-radius: 8px;
                min-width: 140px;
            }}
        """)
        return card, value