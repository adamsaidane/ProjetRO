"""
Script pour charger automatiquement l'exemple avec pénuries dans l'interface
Utilisation: Modifiez interface.py pour appeler ce script
"""

import numpy as np
from PySide6.QtWidgets import QTableWidgetItem

def charger_exemple_penuries(main_window):
    """
    Charge l'exemple avec pénuries dans l'interface
    
    Args:
        main_window: Instance de MainWindow
    """
    
    # Configuration: 3 périodes, 3 fournisseurs, 4 centrales
    main_window.spin_periodes.setValue(3)
    main_window.spin_fournisseurs.setValue(3)
    main_window.spin_centrales.setValue(4)
    
    # Paramètres généraux
    main_window.spin_capacite_stock.setValue(20000)
    main_window.spin_stock_initial.setValue(3000)
    main_window.spin_stock_final.setValue(2000)
    main_window.spin_taux.setValue(0.05)
    main_window.spin_cout_penurie.setValue(500)
    main_window.spin_qte_min.setValue(500)
    
    # Mettre à jour les tableaux
    main_window.update_tables_size()
    
    # Prix d'achat (conçu pour utiliser tous les fournisseurs)
    prix = [
        [100, 105, 98],   # Période 1
        [95, 102, 110],   # Période 2
        [108, 97, 103]    # Période 3
    ]
    
    for t in range(3):
        for s in range(3):
            item = QTableWidgetItem(str(prix[t][s]))
            main_window.table_prix.setItem(t, s, item)
    
    # Coûts fixes
    couts_fixes = [5000, 4500, 5500]
    for s in range(3):
        item = QTableWidgetItem(str(couts_fixes[s]))
        main_window.table_cout_fixe.setItem(0, s, item)
    
    # Coûts de stockage
    for t in range(3):
        item = QTableWidgetItem("2.5")
        main_window.table_cout_stock.setItem(0, t, item)
    
    # Demande TRÈS ÉLEVÉE (pour créer des pénuries)
    demande = [
        [4000, 4500, 3800, 5000],  # Période 1: 17,300 tonnes
        [4200, 4300, 4000, 4800],  # Période 2: 17,300 tonnes
        [3900, 4600, 3700, 5100]   # Période 3: 17,300 tonnes
    ]
    
    for t in range(3):
        for c in range(4):
            item = QTableWidgetItem(str(demande[t][c]))
            main_window.table_demande.setItem(t, c, item)
    
    # Capacité fournisseurs LIMITÉE (max 15,000 par période)
    capacite = [
        [5000, 6000, 4000],  # Période 1
        [5000, 6000, 4000],  # Période 2
        [5000, 6000, 4000]   # Période 3
    ]
    
    for t in range(3):
        for s in range(3):
            item = QTableWidgetItem(str(capacite[t][s]))
            main_window.table_capacite.setItem(t, s, item)
    
    main_window.status_label.setText("✅ Exemple avec pénuries chargé - Demande: 17,300 tonnes > Capacité: 15,000 tonnes")
    
    print("="*70)
    print("✅ EXEMPLE AVEC PÉNURIES CHARGÉ!")
    print("="*70)
    print("\n📊 Configuration:")
    print("   • 3 périodes, 3 fournisseurs, 4 centrales")
    print("   • Demande totale par période: 17,300 tonnes")
    print("   • Capacité totale disponible: 15,000 tonnes")
    print("   • Déficit: 2,300 tonnes par période")
    print("\n⚠️  PÉNURIES ATTENDUES!")
    print("\n🚀 Cliquez sur 'Lancer l'Optimisation' pour voir les résultats")
    print("="*70)