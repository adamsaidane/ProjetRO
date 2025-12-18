"""
Interface graphique pour l'application de gestion de carburant
Utilise PySide6 (PyQt6) pour l'interface utilisateur
"""

from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                               QLabel, QPushButton, QTableWidget, QTableWidgetItem,
                               QSpinBox, QDoubleSpinBox, QGroupBox, QTabWidget,
                               QTextEdit, QProgressBar, QMessageBox, QFormLayout,
                               QHeaderView)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from worker import OptimizationWorker

class MainWindow(QMainWindow):
    """Fenêtre principale de l'application"""
    
    def __init__(self):
        super().__init__()
        
        # Apply light theme styling
        self.setStyleSheet("""
            QMainWindow {
                background-color: white;
            }
            QWidget {
                background-color: white;
                color: black;
            }
            QLabel {
                background-color: white;
                color: black;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #cccccc;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
                background-color: white;
                color: black;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                background-color: white;
                color: black;
            }
            QTableWidget {
                background-color: white;
                color: black;
                gridline-color: #dddddd;
                border: 1px solid #cccccc;
            }
            QHeaderView::section {
                background-color: #f0f0f0;
                color: black;
                padding: 4px;
                border: 1px solid #cccccc;
                font-weight: bold;
            }
            QTabWidget::pane {
                border: 1px solid #cccccc;
                background-color: white;
            }
            QTabBar::tab {
                background-color: #e0e0e0;
                color: black;
                padding: 8px 16px;
                margin-right: 2px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
            QTabBar::tab:selected {
                background-color: white;
                color: black;
                border-bottom-color: white;
            }
            QTabBar::tab:hover {
                background-color: #f0f0f0;
            }
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
            QPushButton#btn_exemple {
                background-color: #FF9800;
            }
            QPushButton#btn_exemple:hover {
                background-color: #f57c00;
            }
            QPushButton#btn_reset {
                background-color: #757575;
            }
            QPushButton#btn_reset:hover {
                background-color: #616161;
            }
            QSpinBox, QDoubleSpinBox {
                background-color: white;
                color: black;
                border: 1px solid #cccccc;
                padding: 4px;
                border-radius: 3px;
            }
            QTextEdit {
                background-color: white;
                color: black;
                border: 1px solid #cccccc;
                font-family: 'Courier New';
            }
            QProgressBar {
                border: 1px solid #cccccc;
                border-radius: 3px;
                text-align: center;
                background-color: white;
                color: black;
            }
            QProgressBar::chunk {
                background-color: #4CAF50;
                width: 10px;
            }
        """)
        
        self.setWindowTitle("Gestion Multi-Période des Stocks de Carburant - Centrales Électriques")
        self.setGeometry(100, 100, 1400, 900)
        
        # Variables pour stocker les données
        self.data = {}
        self.results = None
        self.worker = None
        
        # Créer l'interface
        self.init_ui()
        
        # Initialiser avec des valeurs par défaut
        self.set_default_values()
    
    def init_ui(self):
        """Initialise l'interface utilisateur"""
        central_widget = QWidget()
        central_widget.setStyleSheet("background-color: white;")
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(10, 10, 10, 10)
        central_widget.setLayout(main_layout)
        
        # Titre
        title = QLabel("Ordonnancement Multi-Période - Gestion des Stocks de Carburant")
        title.setFont(QFont('Arial', 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: black; background-color: white;")
        main_layout.addWidget(title)
        
        # Onglets
        tabs = QTabWidget()
        tabs.setStyleSheet("background-color: white;")
        main_layout.addWidget(tabs)
        
        # Onglet 1: Paramètres généraux
        tab_params = self.create_params_tab()
        tabs.addTab(tab_params, "📊 Paramètres Généraux")
        
        # Onglet 2: Prix et coûts
        tab_costs = self.create_costs_tab()
        tabs.addTab(tab_costs, "💰 Prix et Coûts")
        
        # Onglet 3: Demandes et capacités
        tab_demand = self.create_demand_tab()
        tabs.addTab(tab_demand, "📈 Demandes et Capacités")
        
        # Onglet 4: Résultats
        tab_results = self.create_results_tab()
        tabs.addTab(tab_results, "✅ Résultats")
        
        # Onglet 5: Graphiques (NOUVEAU!)
        tab_graphs = self.create_graphs_tab()
        tabs.addTab(tab_graphs, "📊 Graphiques")
        
        # Stocker la référence aux onglets
        self.tabs = tabs
        
        # Boutons d'action
        buttons_layout = QHBoxLayout()
        
        self.btn_optimize = QPushButton("🚀 Lancer l'Optimisation")
        self.btn_optimize.setStyleSheet("""
            background-color: #4CAF50; 
            color: white; 
            padding: 12px 24px; 
            font-size: 14px;
            font-weight: bold;
            border-radius: 6px;
        """)
        self.btn_optimize.clicked.connect(self.run_optimization)
        buttons_layout.addWidget(self.btn_optimize)
        
        self.btn_exemple = QPushButton("⚠️ Exemple avec Pénuries")
        self.btn_exemple.setObjectName("btn_exemple")
        self.btn_exemple.setStyleSheet("""
            background-color: #FF9800; 
            color: white; 
            padding: 12px 24px; 
            font-size: 14px;
            font-weight: bold;
            border-radius: 6px;
        """)
        self.btn_exemple.clicked.connect(self.load_exemple_penurie)
        buttons_layout.addWidget(self.btn_exemple)
        
        self.btn_reset = QPushButton("🔄 Réinitialiser")
        self.btn_reset.setObjectName("btn_reset")
        self.btn_reset.setStyleSheet("""
            background-color: #757575; 
            color: white; 
            padding: 12px 24px; 
            font-size: 14px;
            font-weight: bold;
            border-radius: 6px;
        """)
        self.btn_reset.clicked.connect(self.set_default_values)
        buttons_layout.addWidget(self.btn_reset)
        
        buttons_layout.addStretch()
        main_layout.addLayout(buttons_layout)
        
        # Barre de progression
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #cccccc;
                border-radius: 5px;
                text-align: center;
                height: 25px;
                font-weight: bold;
                color: black;
            }
            QProgressBar::chunk {
                background-color: #4CAF50;
                border-radius: 3px;
            }
        """)
        main_layout.addWidget(self.progress_bar)
        
        # Barre de statut
        self.status_label = QLabel("Prêt")
        self.status_label.setStyleSheet("""
            padding: 10px;
            background-color: #e8f5e8;
            border: 1px solid #c8e6c9;
            border-radius: 4px;
            color: #2e7d32;
            font-weight: bold;
        """)
        main_layout.addWidget(self.status_label)
        
        # Configuration du style Matplotlib pour les graphiques (thème clair)
        plt.style.use('seaborn-v0_8-whitegrid')
        plt.rcParams['figure.facecolor'] = 'white'
        plt.rcParams['axes.facecolor'] = 'white'
        plt.rcParams['axes.edgecolor'] = 'black'
        plt.rcParams['axes.labelcolor'] = 'black'
        plt.rcParams['xtick.color'] = 'black'
        plt.rcParams['ytick.color'] = 'black'
        plt.rcParams['text.color'] = 'black'
        plt.rcParams['grid.color'] = '#dddddd'
    
    def create_params_tab(self):
        """Crée l'onglet des paramètres généraux"""
        widget = QWidget()
        widget.setStyleSheet("background-color: white;")
        layout = QFormLayout()
        
        # Nombre de périodes
        self.spin_periodes = QSpinBox()
        self.spin_periodes.setRange(1, 24)
        self.spin_periodes.setValue(12)
        self.spin_periodes.setStyleSheet("background-color: white; color: black;")
        self.spin_periodes.valueChanged.connect(self.update_tables_size)
        layout.addRow("Nombre de périodes (mois):", self.spin_periodes)
        
        # Nombre de fournisseurs
        self.spin_fournisseurs = QSpinBox()
        self.spin_fournisseurs.setRange(1, 10)
        self.spin_fournisseurs.setValue(3)
        self.spin_fournisseurs.setStyleSheet("background-color: white; color: black;")
        self.spin_fournisseurs.valueChanged.connect(self.update_tables_size)
        layout.addRow("Nombre de fournisseurs:", self.spin_fournisseurs)
        
        # Nombre de centrales
        self.spin_centrales = QSpinBox()
        self.spin_centrales.setRange(1, 10)
        self.spin_centrales.setValue(4)
        self.spin_centrales.setStyleSheet("background-color: white; color: black;")
        self.spin_centrales.valueChanged.connect(self.update_tables_size)
        layout.addRow("Nombre de centrales:", self.spin_centrales)
        
        # Capacité de stockage
        self.spin_capacite_stock = QDoubleSpinBox()
        self.spin_capacite_stock.setRange(0, 1000000)
        self.spin_capacite_stock.setValue(50000)
        self.spin_capacite_stock.setSuffix(" tonnes")
        self.spin_capacite_stock.setStyleSheet("background-color: white; color: black;")
        layout.addRow("Capacité de stockage:", self.spin_capacite_stock)
        
        # Stock initial
        self.spin_stock_initial = QDoubleSpinBox()
        self.spin_stock_initial.setRange(0, 1000000)
        self.spin_stock_initial.setValue(20000)
        self.spin_stock_initial.setSuffix(" tonnes")
        self.spin_stock_initial.setStyleSheet("background-color: white; color: black;")
        layout.addRow("Stock initial:", self.spin_stock_initial)
        
        # Stock final minimum
        self.spin_stock_final = QDoubleSpinBox()
        self.spin_stock_final.setRange(0, 1000000)
        self.spin_stock_final.setValue(15000)
        self.spin_stock_final.setSuffix(" tonnes")
        self.spin_stock_final.setStyleSheet("background-color: white; color: black;")
        layout.addRow("Stock final minimum:", self.spin_stock_final)
        
        # Taux d'actualisation
        self.spin_taux = QDoubleSpinBox()
        self.spin_taux.setRange(0, 1)
        self.spin_taux.setValue(0.05)
        self.spin_taux.setSingleStep(0.01)
        self.spin_taux.setSuffix(" (5%)")
        self.spin_taux.setStyleSheet("background-color: white; color: black;")
        layout.addRow("Taux d'actualisation:", self.spin_taux)
        
        # Coût de pénurie
        self.spin_cout_penurie = QDoubleSpinBox()
        self.spin_cout_penurie.setRange(0, 100000)
        self.spin_cout_penurie.setValue(500)
        self.spin_cout_penurie.setSuffix(" €/tonne")
        self.spin_cout_penurie.setStyleSheet("background-color: white; color: black;")
        layout.addRow("Coût de pénurie:", self.spin_cout_penurie)
        
        # Quantité minimale de commande
        self.spin_qte_min = QDoubleSpinBox()
        self.spin_qte_min.setRange(0, 10000)
        self.spin_qte_min.setValue(1000)
        self.spin_qte_min.setSuffix(" tonnes")
        self.spin_qte_min.setStyleSheet("background-color: white; color: black;")
        layout.addRow("Quantité min. de commande:", self.spin_qte_min)
        
        widget.setLayout(layout)
        return widget
    
    def create_costs_tab(self):
        """Crée l'onglet des prix et coûts"""
        widget = QWidget()
        widget.setStyleSheet("background-color: white;")
        layout = QVBoxLayout()
        
        # Prix d'achat par période et fournisseur
        group_prix = QGroupBox("Prix d'achat (€/tonne) par période et fournisseur")
        group_prix.setStyleSheet("color: black;")
        layout_prix = QVBoxLayout()
        self.table_prix = QTableWidget()
        self.table_prix.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_prix.setStyleSheet("""
            QTableWidget {
                background-color: white;
                color: black;
                gridline-color: #e0e0e0;
            }
            QHeaderView::section {
                background-color: #f5f5f5;
                color: black;
            }
        """)
        layout_prix.addWidget(self.table_prix)
        group_prix.setLayout(layout_prix)
        layout.addWidget(group_prix)
        
        # Coûts fixes de commande
        group_fixe = QGroupBox("Coûts fixes de commande (€) par fournisseur")
        group_fixe.setStyleSheet("color: black;")
        layout_fixe = QVBoxLayout()
        self.table_cout_fixe = QTableWidget()
        self.table_cout_fixe.setRowCount(1)
        self.table_cout_fixe.setVerticalHeaderLabels(["Coût fixe"])
        self.table_cout_fixe.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_cout_fixe.setStyleSheet("""
            QTableWidget {
                background-color: white;
                color: black;
                gridline-color: #e0e0e0;
            }
            QHeaderView::section {
                background-color: #f5f5f5;
                color: black;
            }
        """)
        layout_fixe.addWidget(self.table_cout_fixe)
        group_fixe.setLayout(layout_fixe)
        layout.addWidget(group_fixe)
        
        # Coûts de stockage
        group_stock = QGroupBox("Coûts de stockage (€/tonne) par période")
        group_stock.setStyleSheet("color: black;")
        layout_stock = QVBoxLayout()
        self.table_cout_stock = QTableWidget()
        self.table_cout_stock.setRowCount(1)
        self.table_cout_stock.setVerticalHeaderLabels(["Coût stockage"])
        self.table_cout_stock.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_cout_stock.setStyleSheet("""
            QTableWidget {
                background-color: white;
                color: black;
                gridline-color: #e0e0e0;
            }
            QHeaderView::section {
                background-color: #f5f5f5;
                color: black;
            }
        """)
        layout_stock.addWidget(self.table_cout_stock)
        group_stock.setLayout(layout_stock)
        layout.addWidget(group_stock)
        
        widget.setLayout(layout)
        return widget
    
    def create_demand_tab(self):
        """Crée l'onglet des demandes et capacités"""
        widget = QWidget()
        widget.setStyleSheet("background-color: white;")
        layout = QVBoxLayout()
        
        # Demande par centrale et période
        group_demande = QGroupBox("Demande (tonnes) par centrale et période")
        group_demande.setStyleSheet("color: black;")
        layout_demande = QVBoxLayout()
        self.table_demande = QTableWidget()
        self.table_demande.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_demande.setStyleSheet("""
            QTableWidget {
                background-color: white;
                color: black;
                gridline-color: #e0e0e0;
            }
            QHeaderView::section {
                background-color: #f5f5f5;
                color: black;
            }
        """)
        layout_demande.addWidget(self.table_demande)
        group_demande.setLayout(layout_demande)
        layout.addWidget(group_demande)
        
        # Capacité des fournisseurs
        group_capacite = QGroupBox("Capacité (tonnes) par fournisseur et période")
        group_capacite.setStyleSheet("color: black;")
        layout_capacite = QVBoxLayout()
        self.table_capacite = QTableWidget()
        self.table_capacite.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_capacite.setStyleSheet("""
            QTableWidget {
                background-color: white;
                color: black;
                gridline-color: #e0e0e0;
            }
            QHeaderView::section {
                background-color: #f5f5f5;
                color: black;
            }
        """)
        layout_capacite.addWidget(self.table_capacite)
        group_capacite.setLayout(layout_capacite)
        layout.addWidget(group_capacite)
        
        widget.setLayout(layout)
        return widget
    
    def create_results_tab(self):
        """Crée l'onglet des résultats (TEXTE UNIQUEMENT)"""
        widget = QWidget()
        widget.setStyleSheet("background-color: white;")
        layout = QVBoxLayout()
        
        # Titre
        title_label = QLabel("📊 Résultats de l'Optimisation")
        title_label.setFont(QFont('Arial', 12, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("color: black; background-color: white;")
        layout.addWidget(title_label)
        
        # Résultats textuels - TOUTE LA ZONE
        self.text_results = QTextEdit()
        self.text_results.setReadOnly(True)
        self.text_results.setFont(QFont('Courier', 10))
        self.text_results.setStyleSheet("background-color: white; color: black;")
        layout.addWidget(self.text_results)
        
        widget.setLayout(layout)
        return widget
    
    def create_graphs_tab(self):
        """Crée l'onglet des graphiques (NOUVEAU!)"""
        widget = QWidget()
        widget.setStyleSheet("background-color: white;")
        layout = QVBoxLayout()
        
        # Titre
        title_label = QLabel("📈 Visualisation Graphique des Résultats")
        title_label.setFont(QFont('Arial', 12, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("color: black; background-color: white; padding: 10px;")
        layout.addWidget(title_label)
        
        # Canvas pour les graphiques
        self.figure = Figure(figsize=(14, 7))
        self.figure.patch.set_facecolor('white')
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setStyleSheet("background-color: white; border: 1px solid #cccccc;")
        layout.addWidget(self.canvas)
        
        widget.setLayout(layout)
        return widget
    
    def update_tables_size(self):
        """Met à jour la taille des tableaux selon les paramètres"""
        T = self.spin_periodes.value()
        S = self.spin_fournisseurs.value()
        C = self.spin_centrales.value()
        
        # Table prix d'achat
        self.table_prix.setRowCount(T)
        self.table_prix.setColumnCount(S)
        self.table_prix.setVerticalHeaderLabels([f"Période {t+1}" for t in range(T)])
        self.table_prix.setHorizontalHeaderLabels([f"Fourn. {s+1}" for s in range(S)])
        
        # Table coûts fixes
        self.table_cout_fixe.setColumnCount(S)
        self.table_cout_fixe.setHorizontalHeaderLabels([f"Fourn. {s+1}" for s in range(S)])
        
        # Table coûts de stockage
        self.table_cout_stock.setColumnCount(T)
        self.table_cout_stock.setHorizontalHeaderLabels([f"Période {t+1}" for t in range(T)])
        
        # Table demande
        self.table_demande.setRowCount(T)
        self.table_demande.setColumnCount(C)
        self.table_demande.setVerticalHeaderLabels([f"Période {t+1}" for t in range(T)])
        self.table_demande.setHorizontalHeaderLabels([f"Centrale {c+1}" for c in range(C)])
        
        # Table capacité fournisseurs
        self.table_capacite.setRowCount(T)
        self.table_capacite.setColumnCount(S)
        self.table_capacite.setVerticalHeaderLabels([f"Période {t+1}" for t in range(T)])
        self.table_capacite.setHorizontalHeaderLabels([f"Fourn. {s+1}" for s in range(S)])
    
    def set_default_values(self):
        """Remplit les tableaux avec des valeurs par défaut"""
        self.update_tables_size()
        
        T = self.spin_periodes.value()
        S = self.spin_fournisseurs.value()
        C = self.spin_centrales.value()
        
        # Prix d'achat (variation saisonnière)
        base_prices = [100, 95, 110]
        for t in range(T):
            seasonal_factor = 1 + 0.1 * np.sin(2 * np.pi * t / 12)
            for s in range(S):
                price = base_prices[s % 3] * seasonal_factor
                item = QTableWidgetItem(f"{price:.2f}")
                item.setForeground(Qt.black)
                self.table_prix.setItem(t, s, item)
        
        # Coûts fixes
        fixed_costs = [5000, 4500, 5500]
        for s in range(S):
            item = QTableWidgetItem(f"{fixed_costs[s % 3]}")
            item.setForeground(Qt.black)
            self.table_cout_fixe.setItem(0, s, item)
        
        # Coûts de stockage
        for t in range(T):
            item = QTableWidgetItem("2.5")
            item.setForeground(Qt.black)
            self.table_cout_stock.setItem(0, t, item)
        
        # Demande par centrale (variation)
        base_demands = [3000, 3500, 2800, 4000]
        for t in range(T):
            seasonal_factor = 1 + 0.2 * np.sin(2 * np.pi * t / 12 + np.pi/4)
            for c in range(C):
                demand = base_demands[c % 4] * seasonal_factor
                item = QTableWidgetItem(f"{demand:.0f}")
                item.setForeground(Qt.black)
                self.table_demande.setItem(t, c, item)
        
        # Capacité des fournisseurs
        capacities = [8000, 10000, 7000]
        for t in range(T):
            for s in range(S):
                capacity = capacities[s % 3]
                item = QTableWidgetItem(f"{capacity}")
                item.setForeground(Qt.black)
                self.table_capacite.setItem(t, s, item)
        
        self.status_label.setText("✅ Valeurs par défaut chargées")
        self.status_label.setStyleSheet("""
            padding: 10px;
            background-color: #e8f5e8;
            border: 1px solid #c8e6c9;
            border-radius: 4px;
            color: #2e7d32;
            font-weight: bold;
        """)
    
    def load_exemple_penurie(self):
        """Charge l'exemple avec pénuries"""
        self.spin_periodes.setValue(3)
        self.spin_fournisseurs.setValue(3)
        self.spin_centrales.setValue(4)
        
        self.spin_capacite_stock.setValue(20000)
        self.spin_stock_initial.setValue(3000)
        self.spin_stock_final.setValue(2000)
        self.spin_taux.setValue(0.05)
        self.spin_cout_penurie.setValue(500)
        self.spin_qte_min.setValue(500)
        
        self.update_tables_size()
        
        prix = [[100, 105, 98], [95, 102, 110], [108, 97, 103]]
        for t in range(3):
            for s in range(3):
                item = QTableWidgetItem(str(prix[t][s]))
                item.setForeground(Qt.black)
                self.table_prix.setItem(t, s, item)
        
        couts_fixes = [5000, 4500, 5500]
        for s in range(3):
            item = QTableWidgetItem(str(couts_fixes[s]))
            item.setForeground(Qt.black)
            self.table_cout_fixe.setItem(0, s, item)
        
        for t in range(3):
            item = QTableWidgetItem("2.5")
            item.setForeground(Qt.black)
            self.table_cout_stock.setItem(0, t, item)
        
        demande = [[4000, 4500, 3800, 5000], [4200, 4300, 4000, 4800], [3900, 4600, 3700, 5100]]
        for t in range(3):
            for c in range(4):
                item = QTableWidgetItem(str(demande[t][c]))
                item.setForeground(Qt.black)
                self.table_demande.setItem(t, c, item)
        
        capacite = [[5000, 6000, 4000], [5000, 6000, 4000], [5000, 6000, 4000]]
        for t in range(3):
            for s in range(3):
                item = QTableWidgetItem(str(capacite[t][s]))
                item.setForeground(Qt.black)
                self.table_capacite.setItem(t, s, item)
        
        self.status_label.setText("⚠️ Exemple chargé: Demande 17,300t > Capacité 15,000t → PÉNURIES!")
        self.status_label.setStyleSheet("""
            padding: 10px;
            background-color: #fff3e0;
            border: 1px solid #ffcc80;
            border-radius: 4px;
            color: #f57c00;
            font-weight: bold;
        """)
        
        QMessageBox.information(
            self, "Exemple avec Pénuries Chargé",
            "📊 Configuration:\n\n"
            "• 3 périodes, 3 fournisseurs, 4 centrales\n"
            "• Demande totale: 17,300 tonnes/période\n"
            "• Capacité totale: 15,000 tonnes/période\n"
            "• Déficit: 2,300 tonnes/période\n\n"
            "⚠️ Les pénuries sont INÉVITABLES!\n\n"
            "🚀 Cliquez sur 'Lancer l'Optimisation'\n"
            "   puis consultez les onglets 'Résultats' et 'Graphiques'"
        )
    
    def collect_data(self):
        """Collecte toutes les données de l'interface"""
        T = self.spin_periodes.value()
        S = self.spin_fournisseurs.value()
        C = self.spin_centrales.value()
        
        prix_achat = np.zeros((T, S))
        for t in range(T):
            for s in range(S):
                item = self.table_prix.item(t, s)
                prix_achat[t, s] = float(item.text()) if item else 100.0
        
        cout_fixe = np.zeros(S)
        for s in range(S):
            item = self.table_cout_fixe.item(0, s)
            cout_fixe[s] = float(item.text()) if item else 5000.0
        
        cout_stock = np.zeros(T)
        for t in range(T):
            item = self.table_cout_stock.item(0, t)
            cout_stock[t] = float(item.text()) if item else 2.5
        
        demande = np.zeros((T, C))
        for t in range(T):
            for c in range(C):
                item = self.table_demande.item(t, c)
                demande[t, c] = float(item.text()) if item else 3000.0
        
        capacite = np.zeros((T, S))
        for t in range(T):
            for s in range(S):
                item = self.table_capacite.item(t, s)
                capacite[t, s] = float(item.text()) if item else 8000.0
        
        self.data = {
            'nb_periodes': T,
            'nb_fournisseurs': S,
            'nb_centrales': C,
            'prix_achat': prix_achat,
            'cout_fixe_commande': cout_fixe,
            'cout_stockage': cout_stock,
            'demande_centrales': demande,
            'capacite_fournisseur': capacite,
            'capacite_stockage': self.spin_capacite_stock.value(),
            'stock_initial': self.spin_stock_initial.value(),
            'stock_final_min': self.spin_stock_final.value(),
            'taux_actualisation': self.spin_taux.value(),
            'cout_penurie': self.spin_cout_penurie.value(),
            'qte_min_commande': self.spin_qte_min.value()
        }
        
        return self.data
    
    def run_optimization(self):
        """Lance l'optimisation"""
        self.collect_data()
        
        self.btn_optimize.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)
        self.status_label.setText("⏳ Optimisation en cours...")
        self.status_label.setStyleSheet("""
            padding: 10px;
            background-color: #e3f2fd;
            border: 1px solid #90caf9;
            border-radius: 4px;
            color: #1565c0;
            font-weight: bold;
        """)
        
        self.worker = OptimizationWorker(self.data)
        self.worker.finished.connect(self.on_optimization_finished)
        self.worker.error.connect(self.on_optimization_error)
        self.worker.start()
    
    def on_optimization_finished(self, results):
        """Callback fin d'optimisation"""
        self.results = results
        self.btn_optimize.setEnabled(True)
        self.progress_bar.setVisible(False)
        self.status_label.setText("✅ Optimisation terminée avec succès!")
        self.status_label.setStyleSheet("""
            padding: 10px;
            background-color: #e8f5e8;
            border: 1px solid #c8e6c9;
            border-radius: 4px;
            color: #2e7d32;
            font-weight: bold;
        """)
        
        self.display_results()
    
    def on_optimization_error(self, error_msg):
        """Callback erreur"""
        self.btn_optimize.setEnabled(True)
        self.progress_bar.setVisible(False)
        self.status_label.setText("❌ Erreur lors de l'optimisation")
        self.status_label.setStyleSheet("""
            padding: 10px;
            background-color: #ffebee;
            border: 1px solid #ffcdd2;
            border-radius: 4px;
            color: #c62828;
            font-weight: bold;
        """)
        
        QMessageBox.critical(self, "Erreur", f"Erreur d'optimisation:\n{error_msg}")
    
    def display_results(self):
        """Affiche les résultats"""
        if not self.results:
            return
        
        text = f"""
╔══════════════════════════════════════════════════════════════╗
║           RÉSULTATS DE L'OPTIMISATION                        ║
╚══════════════════════════════════════════════════════════════╝

📊 Coût Total Optimal: {self.results['cout_optimal']:,.2f} €
✅ Statut: {self.results['status']}
📈 Gap d'optimalité: {self.results['gap']*100:.4f}%

═══════════════════════════════════════════════════════════════

SYNTHÈSE PAR PÉRIODE:
"""
        
        T = self.data['nb_periodes']
        S = self.data['nb_fournisseurs']
        C = self.data['nb_centrales']
        
        achats, stocks, consommation, penuries, commandes = self.worker.model.get_solution_arrays(T, S, C)
        
        for t in range(T):
            text += f"\n📅 Période {t+1}:\n"
            text += f"   • Total acheté: {achats[t].sum():,.0f} tonnes\n"
            text += f"   • Stock final: {stocks[t]:,.0f} tonnes\n"
            text += f"   • Consommation totale: {consommation[t].sum():,.0f} tonnes\n"
            if penuries[t].sum() > 0:
                text += f"   ⚠️  Pénurie totale: {penuries[t].sum():,.0f} tonnes\n"
        
        text += f"\n\n{'═'*63}\nACHATS PAR FOURNISSEUR:\n{'═'*63}\n"
        for s in range(S):
            total_achats = achats[:, s].sum()
            periodes_utilisees = [t+1 for t in range(T) if commandes[t,s] > 0.5]
            if periodes_utilisees:
                text += f"\n🏭 Fournisseur {s+1}:\n"
                text += f"   • Total acheté: {total_achats:,.0f} tonnes\n"
                text += f"   • Utilisé aux périodes: {periodes_utilisees}\n"
        
        total_penuries = penuries.sum()
        if total_penuries > 0:
            text += f"\n\n{'═'*63}\n⚠️  PÉNURIES:\n{'═'*63}\n"
            text += f"Total des pénuries: {total_penuries:,.0f} tonnes\n"
            text += f"Coût des pénuries: {total_penuries * self.data['cout_penurie']:,.0f} €\n"
        else:
            text += f"\n\n✅ Aucune pénurie - Toutes les demandes sont satisfaites!\n"
        
        text += f"\n{'═'*63}\n💡 Allez dans l'onglet '📊 Graphiques' pour la visualisation\n{'═'*63}\n"
        
        self.text_results.setText(text)
        
        self.plot_results(achats, stocks, consommation, penuries)
        
        self.graph_message.setStyleSheet("""
            padding: 20px; 
            background-color: #c8e6c9; 
            border-radius: 5px; 
            color: #2e7d32;
        """)
    
    def plot_results(self, achats, stocks, consommation, penuries):
        """Crée les graphiques"""
        self.figure.clear()
        
        T = self.data['nb_periodes']
        periodes = range(1, T+1)
        
        ax1 = self.figure.add_subplot(2, 2, 1)
        ax2 = self.figure.add_subplot(2, 2, 2)
        ax3 = self.figure.add_subplot(2, 2, 3)
        ax4 = self.figure.add_subplot(2, 2, 4)
        
        # Graphique 1: Stock
        ax1.plot(periodes, stocks, 'b-o', linewidth=2, markersize=6)
        ax1.axhline(y=self.data['capacite_stockage'], color='r', linestyle='--', label='Capacité max', linewidth=2)
        ax1.axhline(y=self.data['stock_final_min'], color='g', linestyle='--', label='Stock min final', linewidth=2)
        ax1.set_xlabel('Période', fontsize=11, fontweight='bold')
        ax1.set_ylabel('Stock (tonnes)', fontsize=11, fontweight='bold')
        ax1.set_title('Évolution du Stock', fontsize=12, fontweight='bold')
        ax1.grid(True, alpha=0.3)
        ax1.legend(fontsize=9)
        
        # Graphique 2: Achats
        S = self.data['nb_fournisseurs']
        bottom = np.zeros(T)
        colors = plt.cm.Set3(range(S))
        for s in range(S):
            ax2.bar(periodes, achats[:, s], bottom=bottom, label=f'Fourn. {s+1}', color=colors[s], edgecolor='black', linewidth=0.5)
            bottom += achats[:, s]
        ax2.set_xlabel('Période', fontsize=11, fontweight='bold')
        ax2.set_ylabel('Quantité achetée (tonnes)', fontsize=11, fontweight='bold')
        ax2.set_title('Achats par Fournisseur', fontsize=12, fontweight='bold')
        ax2.legend(fontsize=9)
        ax2.grid(True, alpha=0.3, axis='y')

        # Graphique 3: Consommation
        C = self.data['nb_centrales']
        bottom = np.zeros(T)
        colors = plt.cm.Pastel1(range(C))
        for c in range(C):
            ax3.bar(periodes, consommation[:, c], bottom=bottom, label=f'Centrale {c+1}', color=colors[c], edgecolor='black', linewidth=0.5)
            bottom += consommation[:, c]
        ax3.set_xlabel('Période', fontsize=11, fontweight='bold')
        ax3.set_ylabel('Consommation (tonnes)', fontsize=11, fontweight='bold')
        ax3.set_title('Consommation par Centrale', fontsize=12, fontweight='bold')
        ax3.legend(fontsize=9)
        ax3.grid(True, alpha=0.3, axis='y')
        
        # Graphique 4: Pénuries
        total_penuries = penuries.sum(axis=1)
        ax4.bar(periodes, total_penuries, color='red', alpha=0.7, edgecolor='darkred', linewidth=1.5)
        ax4.set_xlabel('Période', fontsize=11, fontweight='bold')
        ax4.set_ylabel('Pénurie (tonnes)', fontsize=11, fontweight='bold')
        ax4.set_title('Pénuries par Période', fontsize=12, fontweight='bold')
        ax4.grid(True, alpha=0.3, axis='y')
        
        for i, (periode, penurie) in enumerate(zip(periodes, total_penuries)):
            if penurie > 0:
                ax4.text(periode, penurie + max(total_penuries)*0.02, f'{penurie:.0f}', 
                        ha='center', va='bottom', fontweight='bold', fontsize=9)
        
        self.figure.tight_layout()
        self.canvas.draw()