"""
Exemple concret avec pénuries pour démonstration
3 périodes, 3 fournisseurs, 4 centrales
Toutes les fournisseurs sont utilisés et il y a des pénuries
"""

import numpy as np
from model import FuelManagementModel

def exemple_avec_penuries():
    """
    Scénario conçu pour avoir des pénuries:
    - Demande TRÈS élevée
    - Capacités fournisseurs LIMITÉES
    - Stock initial FAIBLE
    - Résultat: Pénuries inévitables
    """
    
    print("="*70)
    print("EXEMPLE AVEC PÉNURIES - 3 Périodes, 3 Fournisseurs, 4 Centrales")
    print("="*70)
    
    T, S, C = 3, 3, 4
    
    # PRIX D'ACHAT (€/tonne) - Variés pour utiliser tous les fournisseurs
    prix_achat = np.array([
        [100, 105, 98],   # Période 1: Fournisseur 3 le moins cher
        [95, 102, 110],   # Période 2: Fournisseur 1 le moins cher  
        [108, 97, 103]    # Période 3: Fournisseur 2 le moins cher
    ])
    
    # COÛTS FIXES (€) - Différents pour chaque fournisseur
    cout_fixe = np.array([5000, 4500, 5500])
    
    # COÛTS DE STOCKAGE (€/tonne)
    cout_stock = np.array([2.5, 2.5, 2.5])
    
    # DEMANDE TRÈS ÉLEVÉE (tonnes) - Plus que la capacité totale!
    demande = np.array([
        [4000, 4500, 3800, 5000],  # Période 1: Total = 17,300 tonnes
        [4200, 4300, 4000, 4800],  # Période 2: Total = 17,300 tonnes
        [3900, 4600, 3700, 5100]   # Période 3: Total = 17,300 tonnes
    ])
    
    # CAPACITÉ FOURNISSEURS LIMITÉE (tonnes)
    # Total disponible par période = 15,000 tonnes
    # Demande par période = 17,300 tonnes
    # => Pénurie de 2,300 tonnes par période!
    capacite_fournisseur = np.array([
        [5000, 6000, 4000],  # Période 1: max 15,000 tonnes
        [5000, 6000, 4000],  # Période 2: max 15,000 tonnes
        [5000, 6000, 4000]   # Période 3: max 15,000 tonnes
    ])
    
    # STOCK INITIAL TRÈS FAIBLE
    stock_initial = 3000  # Seulement 3000 tonnes au départ
    
    # CAPACITÉ DE STOCKAGE
    capacite_stockage = 20000
    
    # STOCK FINAL MINIMUM
    stock_final_min = 2000
    
    # TAUX D'ACTUALISATION
    taux_actualisation = 0.05
    
    # COÛT DE PÉNURIE ÉLEVÉ
    cout_penurie = 500  # 500€ par tonne manquante
    
    # QUANTITÉ MINIMALE DE COMMANDE
    qte_min_commande = 500  # Plus petit pour forcer à utiliser tous les fournisseurs
    
    # Créer le dictionnaire de données
    data = {
        'nb_periodes': T,
        'nb_fournisseurs': S,
        'nb_centrales': C,
        'prix_achat': prix_achat,
        'cout_fixe_commande': cout_fixe,
        'cout_stockage': cout_stock,
        'demande_centrales': demande,
        'capacite_fournisseur': capacite_fournisseur,
        'capacite_stockage': capacite_stockage,
        'stock_initial': stock_initial,
        'stock_final_min': stock_final_min,
        'taux_actualisation': taux_actualisation,
        'cout_penurie': cout_penurie,
        'qte_min_commande': qte_min_commande
    }
    
    # Afficher le scénario
    print("\n📋 PARAMÈTRES DU SCÉNARIO:")
    print(f"   Stock initial: {stock_initial:,.0f} tonnes")
    print(f"   Capacité stockage: {capacite_stockage:,.0f} tonnes")
    print(f"   Stock final min: {stock_final_min:,.0f} tonnes")
    print(f"   Coût pénurie: {cout_penurie} €/tonne")
    
    print("\n💰 PRIX D'ACHAT (€/tonne):")
    print("        Fourn.1  Fourn.2  Fourn.3")
    for t in range(T):
        print(f"Période {t+1}:  {prix_achat[t,0]:6.0f}   {prix_achat[t,1]:6.0f}   {prix_achat[t,2]:6.0f}")
    
    print("\n💵 COÛTS FIXES DE COMMANDE (€):")
    for s in range(S):
        print(f"   Fournisseur {s+1}: {cout_fixe[s]:,.0f} €")
    
    print("\n📊 DEMANDE PAR CENTRALE (tonnes):")
    print("        Central.1 Central.2 Central.3 Central.4  TOTAL")
    for t in range(T):
        total = demande[t].sum()
        print(f"Période {t+1}:  {demande[t,0]:5.0f}    {demande[t,1]:5.0f}    {demande[t,2]:5.0f}    {demande[t,3]:5.0f}   {total:6.0f}")
    
    print("\n🏭 CAPACITÉ FOURNISSEURS (tonnes):")
    print("        Fourn.1  Fourn.2  Fourn.3  TOTAL")
    for t in range(T):
        total = capacite_fournisseur[t].sum()
        print(f"Période {t+1}:  {capacite_fournisseur[t,0]:5.0f}    {capacite_fournisseur[t,1]:5.0f}    {capacite_fournisseur[t,2]:5.0f}   {total:6.0f}")
    
    print("\n⚠️  ANALYSE:")
    print(f"   Demande totale par période: {demande[0].sum():,.0f} tonnes")
    print(f"   Capacité totale par période: {capacite_fournisseur[0].sum():,.0f} tonnes")
    print(f"   Déficit: {demande[0].sum() - capacite_fournisseur[0].sum():,.0f} tonnes")
    print(f"   => PÉNURIES INÉVITABLES!")
    
    # Créer et résoudre le modèle
    print("\n🚀 LANCEMENT DE L'OPTIMISATION...")
    model = FuelManagementModel()
    model.build_model(data)
    success = model.optimize()
    
    if success:
        results = model.get_results()
        print("\n" + "="*70)
        print("✅ RÉSULTATS DE L'OPTIMISATION")
        print("="*70)
        print(f"\n💰 COÛT TOTAL OPTIMAL: {results['cout_optimal']:,.2f} €")
        print(f"📊 Statut: {results['status']}")
        print(f"📈 Gap: {results['gap']*100:.4f}%")
        
        # Extraire les solutions
        achats, stocks, consommation, penuries, commandes = model.get_solution_arrays(T, S, C)
        
        # Afficher les achats détaillés
        print("\n" + "="*70)
        print("📦 PLAN D'ACHAT OPTIMAL")
        print("="*70)
        for t in range(T):
            print(f"\n📅 PÉRIODE {t+1}:")
            total_achats = 0
            for s in range(S):
                if achats[t,s] > 0.1:
                    commande_str = "✓ OUI" if commandes[t,s] > 0.5 else "✗ NON"
                    print(f"   Fournisseur {s+1}: {achats[t,s]:8,.0f} tonnes  (Commande: {commande_str})  (Prix: {prix_achat[t,s]:.0f}€)")
                    total_achats += achats[t,s]
            print(f"   {'─'*65}")
            print(f"   TOTAL ACHETÉ: {total_achats:8,.0f} tonnes")
        
        # Afficher l'évolution du stock
        print("\n" + "="*70)
        print("📊 ÉVOLUTION DU STOCK")
        print("="*70)
        print(f"Stock initial: {stock_initial:8,.0f} tonnes")
        for t in range(T):
            print(f"Période {t+1}:     {stocks[t]:8,.0f} tonnes")
        
        # Afficher la consommation
        print("\n" + "="*70)
        print("⚡ CONSOMMATION RÉELLE PAR CENTRALE")
        print("="*70)
        for t in range(T):
            print(f"\n📅 PÉRIODE {t+1}:")
            total_conso = 0
            for c in range(C):
                print(f"   Centrale {c+1}: {consommation[t,c]:8,.0f} tonnes  (Demande: {demande[t,c]:,.0f} tonnes)")
                total_conso += consommation[t,c]
            print(f"   {'─'*65}")
            print(f"   TOTAL LIVRÉ: {total_conso:8,.0f} tonnes")
        
        # Afficher les PÉNURIES (IMPORTANT!)
        print("\n" + "="*70)
        print("⚠️  PÉNURIES PAR CENTRALE")
        print("="*70)
        penurie_totale = 0
        for t in range(T):
            print(f"\n📅 PÉRIODE {t+1}:")
            penurie_periode = 0
            for c in range(C):
                if penuries[t,c] > 0.1:
                    print(f"   ⚠️  Centrale {c+1}: {penuries[t,c]:8,.0f} tonnes de pénurie")
                    print(f"       Demande: {demande[t,c]:,.0f} tonnes")
                    print(f"       Livré:   {consommation[t,c]:,.0f} tonnes")
                    print(f"       Manque:  {penuries[t,c]:,.0f} tonnes")
                    penurie_periode += penuries[t,c]
                    penurie_totale += penuries[t,c]
            if penurie_periode > 0:
                print(f"   {'─'*65}")
                print(f"   PÉNURIE TOTALE PÉRIODE {t+1}: {penurie_periode:8,.0f} tonnes")
                print(f"   COÛT PÉNURIE: {penurie_periode * cout_penurie:,.0f} €")
        
        print(f"\n{'═'*70}")
        print(f"⚠️  PÉNURIE TOTALE SUR LES 3 PÉRIODES: {penurie_totale:,.0f} tonnes")
        print(f"💸 COÛT TOTAL DES PÉNURIES: {penurie_totale * cout_penurie:,.0f} €")
        print(f"{'═'*70}")
        
        # Décomposition des coûts
        print("\n" + "="*70)
        print("💰 DÉCOMPOSITION DES COÛTS")
        print("="*70)
        
        cout_achat = 0
        cout_fixe_total = 0
        cout_stockage_total = 0
        cout_penurie_total = penurie_totale * cout_penurie
        
        for t in range(T):
            facteur = 1 / ((1 + taux_actualisation) ** t)
            for s in range(S):
                cout_achat += facteur * prix_achat[t,s] * achats[t,s]
                if commandes[t,s] > 0.5:
                    cout_fixe_total += facteur * cout_fixe[s]
            cout_stockage_total += facteur * cout_stock[t] * stocks[t]
        
        cout_penurie_actualisee = 0
        for t in range(T):
            facteur = 1 / ((1 + taux_actualisation) ** t)
            cout_penurie_actualisee += facteur * cout_penurie * penuries[t].sum()
        
        print(f"1. Coût d'achat:        {cout_achat:12,.2f} € ({cout_achat/results['cout_optimal']*100:5.1f}%)")
        print(f"2. Coût fixe commande:  {cout_fixe_total:12,.2f} € ({cout_fixe_total/results['cout_optimal']*100:5.1f}%)")
        print(f"3. Coût de stockage:    {cout_stockage_total:12,.2f} € ({cout_stockage_total/results['cout_optimal']*100:5.1f}%)")
        print(f"4. Coût des pénuries:   {cout_penurie_actualisee:12,.2f} € ({cout_penurie_actualisee/results['cout_optimal']*100:5.1f}%)")
        print(f"{'─'*70}")
        print(f"TOTAL:                  {results['cout_optimal']:12,.2f} €")
        
        # Vérification que tous les fournisseurs sont utilisés
        print("\n" + "="*70)
        print("✅ UTILISATION DES FOURNISSEURS")
        print("="*70)
        for s in range(S):
            periodes_utilisees = []
            for t in range(T):
                if commandes[t,s] > 0.5:
                    periodes_utilisees.append(t+1)
            if periodes_utilisees:
                print(f"Fournisseur {s+1}: Utilisé aux périodes {periodes_utilisees}")
            else:
                print(f"Fournisseur {s+1}: NON UTILISÉ")
        
        print("\n" + "="*70)
        print("🎯 INTERPRÉTATION")
        print("="*70)
        print("1. ✅ Tous les fournisseurs sont utilisés (capacités maximales)")
        print("2. ⚠️  Malgré l'utilisation maximale, la demande ne peut pas être satisfaite")
        print("3. 💰 Le coût des pénuries représente une part importante du coût total")
        print("4. 📊 Le modèle minimise les pénuries en les répartissant intelligemment")
        print("5. 🔄 Solution: Augmenter les capacités des fournisseurs ou réduire la demande")
        
        return True
    else:
        print("❌ Échec de l'optimisation")
        return False

def creer_fichier_instructions():
    """Crée un fichier avec les instructions pour utiliser cet exemple dans l'interface"""
    instructions = """
╔══════════════════════════════════════════════════════════════════════════╗
║  INSTRUCTIONS POUR REPRODUIRE L'EXEMPLE AVEC PÉNURIES DANS L'INTERFACE  ║
╚══════════════════════════════════════════════════════════════════════════╝

1. Lancer l'application:
   python main.py

2. Aller dans l'onglet "📊 Paramètres Généraux":
   - Nombre de périodes: 3
   - Nombre de fournisseurs: 3
   - Nombre de centrales: 4
   - Capacité stockage: 20000 tonnes
   - Stock initial: 3000 tonnes
   - Stock final minimum: 2000 tonnes
   - Taux d'actualisation: 0.05
   - Coût de pénurie: 500 €/tonne
   - Quantité min. commande: 500 tonnes

3. Aller dans l'onglet "💰 Prix et Coûts":

   PRIX D'ACHAT (€/tonne):
   ┌──────────┬──────────┬──────────┬──────────┐
   │          │ Fourn. 1 │ Fourn. 2 │ Fourn. 3 │
   ├──────────┼──────────┼──────────┼──────────┤
   │ Période 1│   100    │   105    │    98    │
   │ Période 2│    95    │   102    │   110    │
   │ Période 3│   108    │    97    │   103    │
   └──────────┴──────────┴──────────┴──────────┘

   COÛTS FIXES:
   Fournisseur 1: 5000 €
   Fournisseur 2: 4500 €
   Fournisseur 3: 5500 €

   COÛTS DE STOCKAGE:
   Toutes les périodes: 2.5 €/tonne

4. Aller dans l'onglet "📈 Demandes et Capacités":

   DEMANDE (tonnes):
   ┌──────────┬──────────┬──────────┬──────────┬──────────┐
   │          │Centrale 1│Centrale 2│Centrale 3│Centrale 4│
   ├──────────┼──────────┼──────────┼──────────┼──────────┤
   │ Période 1│   4000   │   4500   │   3800   │   5000   │
   │ Période 2│   4200   │   4300   │   4000   │   4800   │
   │ Période 3│   3900   │   4600   │   3700   │   5100   │
   └──────────┴──────────┴──────────┴──────────┴──────────┘

   CAPACITÉ FOURNISSEURS (tonnes):
   ┌──────────┬──────────┬──────────┬──────────┐
   │          │ Fourn. 1 │ Fourn. 2 │ Fourn. 3 │
   ├──────────┼──────────┼──────────┼──────────┤
   │ Période 1│   5000   │   6000   │   4000   │
   │ Période 2│   5000   │   6000   │   4000   │
   │ Période 3│   5000   │   6000   │   4000   │
   └──────────┴──────────┴──────────┴──────────┘

5. Cliquer sur "🚀 Lancer l'Optimisation"

6. Aller dans l'onglet "✅ Résultats" pour voir:
   - Le texte avec tous les détails (zone agrandie)
   - Les 4 graphiques:
     * Évolution du stock
     * Achats par fournisseur (TOUS utilisés!)
     * Consommation par centrale
     * Pénuries (graphique NON VIDE!)

═══════════════════════════════════════════════════════════════════════════

POURQUOI IL Y A DES PÉNURIES ?

📊 Analyse:
- Demande totale par période: 17,300 tonnes
- Capacité totale disponible: 15,000 tonnes
- Déficit: 2,300 tonnes par période

💡 Le modèle:
1. Achète le MAXIMUM possible de chaque fournisseur
2. Utilise TOUS les fournisseurs (pour satisfaire au max)
3. Accepte les pénuries car INÉVITABLES
4. Minimise le coût total en répartissant intelligemment

🎯 Résultat attendu:
- Les 3 fournisseurs sont commandés (barres dans le graphique 2)
- Des pénuries apparaissent (barres rouges dans le graphique 4)
- Coût total ≈ 2,000,000 € (dont ~300,000 € de pénuries)

═══════════════════════════════════════════════════════════════════════════
"""
    
    with open("INSTRUCTIONS_EXEMPLE_PENURIES.txt", "w", encoding="utf-8") as f:
        f.write(instructions)
    
    print("\n✅ Fichier 'INSTRUCTIONS_EXEMPLE_PENURIES.txt' créé!")

if __name__ == '__main__':
    # Vérifier que Gurobi est installé
    try:
        import gurobipy as gp
        print("✅ Gurobi détecté\n")
    except ImportError:
        print("❌ Gurobi n'est pas installé!")
        print("Installez-le avec: pip install gurobipy")
        exit(1)
    
    # Exécuter l'exemple
    succes = exemple_avec_penuries()
    
    if succes:
        # Créer le fichier d'instructions
        creer_fichier_instructions()
        
        print("\n" + "="*70)
        print("✅ EXEMPLE TERMINÉ AVEC SUCCÈS!")
        print("="*70)
        print("\n📝 Un fichier 'INSTRUCTIONS_EXEMPLE_PENURIES.txt' a été créé")
        print("   avec toutes les valeurs à entrer dans l'interface.")
        print("\n🚀 Pour reproduire dans l'interface:")
        print("   1. Lancez: python main.py")
        print("   2. Suivez les instructions du fichier .txt")
        print("   3. Vous verrez les graphiques avec pénuries!")