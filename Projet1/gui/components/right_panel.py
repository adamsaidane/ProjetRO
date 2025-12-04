from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QPushButton, QProgressBar, QTabWidget,
                             QLabel, QHBoxLayout, QFrame)

from Projet1.gui.components.process_list_tab import ProcessListTab
from Projet1.gui.components.results_tab import ResultsTab
from Projet1.gui.components.visualization_tab import VisualizationTab

class RightPanel(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        right_layout = QVBoxLayout(self)
        right_layout.setContentsMargins(10, 10, 10, 10)
        right_layout.setSpacing(12)

        # Tabs
        tabs = QTabWidget()

        process_tab = ProcessListTab(parent)
        tabs.addTab(process_tab, "Processus")
        self.parent.process_table = process_tab.process_table  # Pour accès depuis main

        results_tab = ResultsTab(parent)
        tabs.addTab(results_tab, "Résultats")
        self.kpi_cpu = results_tab.kpi_cpu
        self.kpi_ram = results_tab.kpi_ram
        self.kpi_threads = results_tab.kpi_threads
        self.kpi_value = results_tab.kpi_value
        self.results_summary = results_tab.results_summary
        self.process_cards_container = results_tab.process_cards_container
        self.process_cards_layout = results_tab.process_cards_layout

        viz_tab = VisualizationTab(parent)
        tabs.addTab(viz_tab, "Graphiques")
        self.matplotlib_widget = viz_tab.matplotlib_widget

        right_layout.addWidget(tabs)

        # Barre de progression
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        right_layout.addWidget(self.progress_bar)

        # Bouton d'optimisation
        optimize_btn = QPushButton("LANCER L'OPTIMISATION")
        optimize_btn.clicked.connect(self.parent.optimize)
        optimize_btn.setStyleSheet("""
            background-color: #9b59b6; 
            color: white; 
            padding: 15px; 
            font-size: 16px; 
            font-weight: bold;
            border-radius: 5px;
        """)
        right_layout.addWidget(optimize_btn)

    def display_results(self, results):
        """Affiche un résumé synthétique"""
        if results:
            # KPI values
            self.kpi_cpu.setText(f"{results.total_cpu:.1f}%")
            self.kpi_ram.setText(f"{results.total_ram:.1f} GB")
            self.kpi_threads.setText(str(results.total_threads))
            if results.objective_value is not None:
                self.kpi_value.setText(f"{results.objective_value:.1f}")
            else:
                self.kpi_value.setText("--")

            # Résumé texte
            summary_lines = []
            summary_lines.append(f"Statut : {results.status}")
            if results.status == 'Optimal':
                summary_lines.append(f"Processus sélectionnés : {len(results.selected_processes)}")
                summary_lines.append(f"CPU utilisé : {results.total_cpu:.1f}% / {self.parent.cpu_max_spin.value()}%")
                summary_lines.append(f"RAM utilisée : {results.total_ram:.1f} GB / {self.parent.ram_max_spin.value():.1f} GB")
                summary_lines.append(f"Threads utilisés : {results.total_threads} / {self.parent.threads_max_spin.value()}")
                summary_lines.append(f"Temps total : {results.total_time} s")
            self.results_summary.setText("  •  " + "  |  ".join(summary_lines))

    def create_process_card(self, proc):
        """Crée une card avec code couleur selon la priorité"""
        # Dictionnaire de couleurs par priorité
        colors = {
            1: ("#e74c3c", "#5c1d16"),  # Critique : Rouge
            2: ("#f39c12", "#633f07"),  # Haute : Orange
            3: ("#3498db", "#163f5c"),  # Normale : Bleu
            4: ("#95a5a6", "#3e4747")  # Basse : Gris
        }

        border_color, icon_bg = colors.get(proc.priority, ("#dddddd", "#222222"))

        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background-color: #1e1e1e;
                border: 2px solid {border_color};
                border-radius: 10px;
            }}
            QLabel {{
                border: none;
                color: #ecf0f1;
            }}
        """)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(15, 12, 15, 12)
        layout.setSpacing(5)

        # Header: Nom et Badge de Priorité
        header_layout = QHBoxLayout()

        title = QLabel(proc.name)
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: white;")
        header_layout.addWidget(title)

        header_layout.addStretch()

        prio_badge = QLabel(self.parent.PRIORITY_NAMES[proc.priority].upper())
        prio_badge.setStyleSheet(f"""
            background-color: {icon_bg};
            color: {border_color};
            border: 1px solid {border_color};
            border-radius: 5px;
            padding: 2px 8px;
            font-size: 10px;
            font-weight: bold;
        """)
        header_layout.addWidget(prio_badge)
        layout.addLayout(header_layout)

        # Metrics: CPU, RAM, Valeur
        metrics = QLabel(
            f"💎 Valeur: <b>{proc.value}</b>  |  "
            f"🖥️ CPU: <b>{proc.cpu:.1f}%</b>  |  "
            f"💾 RAM: <b>{proc.ram:.1f} GB</b>  |  "
            f"🧵 Threads: <b>{proc.threads:.1f} GB</b>  |  "
            f"⏰ Time: <b>{proc.duration:.1f} s</b>"
        )
        metrics.setStyleSheet("font-size: 13px; color: #bdc3c7;")
        layout.addWidget(metrics)

        # Footer: Dépendances & Incompatibilités
        if proc.dependencies or proc.incompatible_with:
            footer_line = QFrame()
            footer_line.setFrameShape(QFrame.Shape.HLine)
            footer_line.setStyleSheet(f"background-color: {border_color}; max-height: 1px; margin-top: 5px;")
            layout.addWidget(footer_line)

            if proc.dependencies:
                deps = QLabel(f"🔗 Dépend de: {', '.join(proc.dependencies)}")
                deps.setStyleSheet("font-size: 11px; color: #3498db;")
                layout.addWidget(deps)

            if proc.incompatible_with:
                incomp = QLabel(f"🚫 Incompatible avec: {', '.join(proc.incompatible_with)}")
                incomp.setStyleSheet("font-size: 11px; color: #e74c3c;")
                layout.addWidget(incomp)

        return card