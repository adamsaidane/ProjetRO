from PyQt6.QtWidgets import QWidget, QVBoxLayout
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from Projet1.utils.styles import CHART_COLORS, PRIORITY_NAMES


class MatplotlibWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        # Création de la figure avec fond sombre profond
        self.figure = Figure(figsize=(10, 8), facecolor=CHART_COLORS['background'])
        self.canvas = FigureCanvas(self.figure)
        layout = QVBoxLayout()
        layout.addWidget(self.canvas)
        self.setLayout(layout)

    def plot_resource_usage(self, results, config):
        self.figure.clear()
        if not results or results.status != 'Optimal':
            self.canvas.draw()
            return

        # Configuration du style sombre global
        plt.rcParams['text.color'] = CHART_COLORS['text']
        plt.rcParams['axes.labelcolor'] = CHART_COLORS['text']

        ax1 = self.figure.add_subplot(121, facecolor=CHART_COLORS['background'])
        ax2 = self.figure.add_subplot(122, facecolor=CHART_COLORS['background'])

        # --- GRAPHIQUE 1 : Saturation (%) en Barres Verticales ---
        categories = ['CPU', 'RAM', 'THREADS']
        used = [results.total_cpu, results.total_ram, results.total_threads]
        limits = [config.cpu_max, config.ram_max, config.threads_max]

        # Calcul du pourcentage d'utilisation
        percentages = [(u / l) * 100 for u, l in zip(used, limits)]

        # Code couleur : Vert < 70%, Jaune < 90%, Rouge >= 90%
        colors = [
            CHART_COLORS['saturation_green'] if p < 70
            else CHART_COLORS['saturation_yellow'] if p < 90
            else CHART_COLORS['saturation_red']
            for p in percentages
        ]

        x_pos = range(len(categories))

        # Barres de fond (Capacité 100%)
        ax1.bar(x_pos, [100] * 3, color=CHART_COLORS['grid'], alpha=0.3, width=0.5)
        # Barres d'utilisation réelle (%)
        bars = ax1.bar(x_pos, percentages, color=colors, width=0.5)

        ax1.set_xticks(x_pos)
        ax1.set_xticklabels(categories, fontweight='bold', color=CHART_COLORS['text'])
        ax1.set_ylim(0, 110)  # Un peu d'espace au dessus pour les labels
        ax1.tick_params(axis='y', colors=CHART_COLORS['text'])
        ax1.spines['bottom'].set_color(CHART_COLORS['text'])
        ax1.spines['left'].set_color(CHART_COLORS['text'])
        ax1.set_ylabel('Saturation (%)')
        ax1.set_title('Utilisation Relative (%)', pad=20, fontsize=12, color=CHART_COLORS['text'])

        # Ajout des étiquettes de pourcentage au-dessus des barres
        for bar, p in zip(bars, percentages):
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width() / 2., height + 2,
                     f'{p:.1f}%', ha='center', va='bottom',
                     color='white', fontweight='bold', fontsize=10)

        # Nettoyage des bordures
        ax1.spines['top'].set_visible(False)
        ax1.spines['right'].set_visible(False)
        ax1.grid(axis='y', linestyle='--', alpha=0.1)

        # --- GRAPHIQUE 2 : Donut de la Valeur ---
        val_per_prio = {1: 0, 2: 0, 3: 0, 4: 0}
        for proc in results.selected_processes:
            val_per_prio[proc.priority] += proc.value

        labels, sizes, colors_prio = [], [], []

        for p in sorted(val_per_prio.keys()):
            if val_per_prio[p] > 0:
                labels.append(PRIORITY_NAMES[p])
                sizes.append(val_per_prio[p])
                colors_prio.append(CHART_COLORS['priority_map'][p])

        if sizes:
            wedges, _, _ = ax2.pie(sizes, labels=labels, autopct='%1.0f%%',
                                   startangle=140, colors=colors_prio,
                                   pctdistance=0.85, textprops={'color': "w"})
            # Style Donut
            centre_circle = plt.Circle((0, 0), 0.70, fc=CHART_COLORS['background'])
            ax2.add_artist(centre_circle)
            ax2.set_title('Apport de Valeur', pad=20, fontsize=12, color=CHART_COLORS['text'])

        self.figure.tight_layout()
        self.canvas.draw()