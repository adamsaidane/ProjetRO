APP_STYLESHEET = """
    QGroupBox {
        font-weight: bold;
        border: 1px solid #cccccc;
        border-radius: 6px;
        margin-top: 10px;
        padding: 10px;
        margin-bottom: 10px;
    }

    QGroupBox::title {
        subcontrol-origin: margin;
        subcontrol-position: top left;
        padding: 2px 6px;
    }

    QLabel {
        font-size: 13px;
    }

    QSpinBox, QDoubleSpinBox, QComboBox {
        padding: 4px;
    }

    QPushButton {
        padding: 8px;
        border-radius: 6px;
        font-weight: bold;
    }

    QTableWidget::item {
        padding: 6px;
    }

    QHeaderView::section {
        padding: 6px;
        border: none;
        background-color: #384548;
        font-weight: bold;
    }

    QTabWidget::pane {
        border: 1px solid #384548;
        border-radius: 6px;
        padding: 4px;
    }

    QTabBar::tab {
        padding: 8px 14px;
        border: 1px solid #384548;
        border-radius: 4px;
    }

    QTabBar::tab:selected {
        background-color: #384548;
        font-weight: bold;
    }
"""

# Style de la table des processus
TABLE_STYLESHEET = """
    QTableWidget {
        alternate-background-color: #28231D;
    }
"""

# Style du scroll area des résultats
SCROLL_AREA_STYLESHEET = """
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
"""

# Style des boutons d'action
BUTTON_STYLES = {
    'add': "background-color: #2ecc71; color: white; padding: 5px; font-weight: bold;",
    'clear': "background-color: #e74c3c; color: white; padding: 5px; font-weight: bold;",
    'load_example': """
        background-color: #3498db; 
        color: white; 
        padding: 8px;
        font-weight: bold;
        border-radius: 4px;
    """,
    'optimize': """
        background-color: #9b59b6; 
        color: white; 
        padding: 15px; 
        font-size: 16px; 
        font-weight: bold;
        border-radius: 5px;
    """,
    'dependency': "padding: 4px; border-radius: 4px; background-color: #3498db;",
    'incompatibility': "padding: 4px; border-radius: 4px; background-color: #f39c12;",
    'delete': "padding: 4px; border-radius: 4px; background-color: #e74c3c;"
}

# Couleurs par priorité pour les cards
PRIORITY_COLORS = {
    1: ("#e74c3c", "#5c1d16"),  # Critique : Rouge
    2: ("#f39c12", "#633f07"),  # Haute : Orange
    3: ("#3498db", "#163f5c"),  # Normale : Bleu
    4: ("#95a5a6", "#3e4747")   # Basse : Gris
}

# Couleurs pour les graphiques
CHART_COLORS = {
    'priority_map': {1: '#e74c3c', 2: '#f39c12', 3: '#3498db', 4: '#95a5a6'},
    'saturation_green': '#2ecc71',
    'saturation_yellow': '#f1c40f',
    'saturation_red': '#e74c3c',
    'background': '#121212',
    'text': '#ecf0f1',
    'grid': '#333333'
}

# Noms des priorités
PRIORITY_NAMES = {1: "Critique", 2: "Haute", 3: "Normale", 4: "Basse"}