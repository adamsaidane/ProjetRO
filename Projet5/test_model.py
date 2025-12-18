"""
Script de test pour valider le modèle d'optimisation
Peut être exécuté sans interface graphique
"""

import numpy as np
from model import FuelManagementModel

def test_simple_case():
    """Test avec un cas simple de 3 périodes"""
    print("=" * 60)
    print("TEST 1: Cas simple (3 périodes, 2 fournisseurs, 2 centrales)")
    print("=" * 60)
    
    T, S, C = 3, 2, 2
    
    data = {
        'nb_periodes': T,
        'nb_fournisseurs': S,
        'nb_centrales': C,
        'prix_achat': np.array([
            [100, 105],  # Période 0
            [102, 103],  # Période 1
            [98, 110]    # Période 2
        ]),
        'cout_fixe_commande': np.array([5000, 4500]),
        'cout_stockage': np.array([2.5, 2.5, 2.5]),
        'demande_centrales': np.array([
            [3000, 3500],  # Période 0
            [3200, 3400],  # Période 1
            [2800, 3600]   # Période 2
        ]),
        'capacite_fournisseur': np.array([
            [8000, 7000],
            [8000, 7000],
            [8000, 7000]
        ]),
        'capacite_stockage': 50000,
        'stock_initial': 10000,
        'stock_final_min': 8000,
        'taux_actualisation': 0.05,
        'cout_penurie': 500,
        'qte_min_commande': 1000
    }
    
    # Créer et résoudre le modèle
    model = FuelManagementModel()
    model.build_model(data)
    success = model.optimize()
    
    if success:
        results = model.get_results()
        print(f"\n✅ Optimisation réussie!")
        print(f"📊 Coût optimal: {results['cout_optimal']:,.2f} €")
        print(f"🎯 Status: {results['status']}")
        
        # Afficher les achats
        achats, stocks, consommation, penuries, commandes = model.get_solution_arrays(T, S, C)
        
        print("\n📦 PLAN D'ACHAT:")
        for t in range(T):
            print(f"\nPériode {t+1}:")
            for s in range(S):
                if achats[t,s] > 0.1:
                    print(f"  Fournisseur {s+1}: {achats[t,s]:,.0f} tonnes (Commande: {'Oui' if commandes[t,s] > 0.5 else 'Non'})")
        
        print("\n📊 ÉVOLUTION DU STOCK:")
        for t in range(T):
            print(f"Période {t+1}: {stocks[t]:,.0f} tonnes")
        
        print("\n⚡ CONSOMMATION:")
        for t in range(T):
            print(f"Période {t+1}:")
            for c in range(C):
                print(f"  Centrale {c+1}: {consommation[t,c]:,.0f} tonnes")
        
        if penuries.sum() > 0:
            print("\n⚠️  PÉNURIES DÉTECTÉES:")
            for t in range(T):
                for c in range(C):
                    if penuries[t,c] > 0.1:
                        print(f"  Période {t+1}, Centrale {c+1}: {penuries[t,c]:,.0f} tonnes")
        else:
            print("\n✅ Aucune pénurie - Toutes les demandes satisfaites")
        
        return True
    else:
        print("❌ Échec de l'optimisation")
        return False

def test_capacity_constraint():
    """Test avec des capacités serrées"""
    print("\n" + "=" * 60)
    print("TEST 2: Capacités serrées")
    print("=" * 60)
    
    T, S, C = 6, 3, 3
    
    data = {
        'nb_periodes': T,
        'nb_fournisseurs': S,
        'nb_centrales': C,
        'prix_achat': np.random.uniform(95, 115, (T, S)),
        'cout_fixe_commande': np.array([5000, 4500, 5500]),
        'cout_stockage': np.full(T, 2.5),
        'demande_centrales': np.random.uniform(2500, 4000, (T, C)),
        'capacite_fournisseur': np.full((T, S), 6000),  # Capacité réduite
        'capacite_stockage': 30000,  # Stockage réduit
        'stock_initial': 15000,
        'stock_final_min': 10000,
        'taux_actualisation': 0.05,
        'cout_penurie': 500,
        'qte_min_commande': 500
    }
    
    model = FuelManagementModel()
    model.build_model(data)
    success = model.optimize()
    
    if success:
        results = model.get_results()
        print(f"\n✅ Optimisation réussie!")
        print(f"📊 Coût optimal: {results['cout_optimal']:,.2f} €")
        
        achats, stocks, consommation, penuries, _ = model.get_solution_arrays(T, S, C)
        
        # Vérifier les contraintes
        print(f"\n🔍 VÉRIFICATION DES CONTRAINTES:")
        print(f"Stock max: {data['capacite_stockage']:.0f} tonnes")
        print(f"Stock final requis: {data['stock_final_min']:.0f} tonnes")
        print(f"Stock final obtenu: {stocks[-1]:.0f} tonnes")
        
        if stocks[-1] >= data['stock_final_min'] - 0.01:
            print("✅ Contrainte de stock final respectée")
        else:
            print("❌ Contrainte de stock final violée")
        
        if np.all(stocks <= data['capacite_stockage'] + 0.01):
            print("✅ Contrainte de capacité de stockage respectée")
        else:
            print("❌ Contrainte de capacité de stockage violée")
        
        return True
    else:
        print("❌ Échec de l'optimisation")
        return False

def test_seasonal_demand():
    """Test avec demande saisonnière"""
    print("\n" + "=" * 60)
    print("TEST 3: Demande saisonnière (12 mois)")
    print("=" * 60)
    
    T, S, C = 12, 3, 4
    
    # Créer une demande saisonnière
    base_demand = np.array([3000, 3500, 2800, 4000])
    demande = np.zeros((T, C))
    for t in range(T):
        seasonal_factor = 1 + 0.3 * np.sin(2 * np.pi * t / 12)
        demande[t] = base_demand * seasonal_factor
    
    # Prix avec variation saisonnière
    base_prices = np.array([100, 95, 110])
    prix_achat = np.zeros((T, S))
    for t in range(T):
        seasonal_factor = 1 + 0.15 * np.sin(2 * np.pi * t / 12 + np.pi/4)
        prix_achat[t] = base_prices * seasonal_factor
    
    data = {
        'nb_periodes': T,
        'nb_fournisseurs': S,
        'nb_centrales': C,
        'prix_achat': prix_achat,
        'cout_fixe_commande': np.array([5000, 4500, 5500]),
        'cout_stockage': np.full(T, 2.5),
        'demande_centrales': demande,
        'capacite_fournisseur': np.full((T, S), 10000),
        'capacite_stockage': 50000,
        'stock_initial': 20000,
        'stock_final_min': 15000,
        'taux_actualisation': 0.05,
        'cout_penurie': 500,
        'qte_min_commande': 1000
    }
    
    model = FuelManagementModel()
    model.build_model(data)
    success = model.optimize()
    
    if success:
        results = model.get_results()
        print(f"\n✅ Optimisation réussie!")
        print(f"📊 Coût optimal: {results['cout_optimal']:,.2f} €")
        
        achats, stocks, consommation, penuries, _ = model.get_solution_arrays(T, S, C)
        
        print(f"\n📈 STATISTIQUES ANNUELLES:")
        print(f"Total acheté: {achats.sum():,.0f} tonnes")
        print(f"Total consommé: {consommation.sum():,.0f} tonnes")
        print(f"Stock moyen: {stocks.mean():,.0f} tonnes")
        print(f"Stock min: {stocks.min():,.0f} tonnes")
        print(f"Stock max: {stocks.max():,.0f} tonnes")
        
        if penuries.sum() > 0:
            print(f"⚠️  Pénurie totale: {penuries.sum():,.0f} tonnes")
        else:
            print("✅ Aucune pénurie sur l'année")
        
        return True
    else:
        print("❌ Échec de l'optimisation")
        return False

def test_performance():
    """Test de performance avec un problème de grande taille"""
    print("\n" + "=" * 60)
    print("TEST 4: Performance (24 périodes, 5 fournisseurs, 8 centrales)")
    print("=" * 60)
    
    import time
    
    T, S, C = 24, 5, 8
    
    data = {
        'nb_periodes': T,
        'nb_fournisseurs': S,
        'nb_centrales': C,
        'prix_achat': np.random.uniform(90, 120, (T, S)),
        'cout_fixe_commande': np.random.uniform(4000, 6000, S),
        'cout_stockage': np.full(T, 2.5),
        'demande_centrales': np.random.uniform(2000, 5000, (T, C)),
        'capacite_fournisseur': np.random.uniform(8000, 12000, (T, S)),
        'capacite_stockage': 100000,
        'stock_initial': 40000,
        'stock_final_min': 30000,
        'taux_actualisation': 0.05,
        'cout_penurie': 500,
        'qte_min_commande': 1000
    }
    
    print(f"Taille du problème:")
    print(f"  - Variables continues: {T*(S+C+1) + T*C}")
    print(f"  - Variables binaires: {T*S}")
    print(f"  - Total variables: {T*(2*S+2*C+1)}")
    
    model = FuelManagementModel()
    
    start_time = time.time()
    model.build_model(data)
    build_time = time.time() - start_time
    
    start_time = time.time()
    success = model.optimize()
    solve_time = time.time() - start_time
    
    print(f"\n⏱️  TEMPS D'EXÉCUTION:")
    print(f"  Construction du modèle: {build_time:.2f} secondes")
    print(f"  Résolution: {solve_time:.2f} secondes")
    print(f"  Total: {build_time + solve_time:.2f} secondes")
    
    if success:
        results = model.get_results()
        print(f"\n✅ Optimisation réussie!")
        print(f"📊 Coût optimal: {results['cout_optimal']:,.2f} €")
        print(f"🎯 Gap: {results['gap']*100:.4f}%")
        return True
    else:
        print("❌ Échec de l'optimisation")
        return False

def run_all_tests():
    """Exécute tous les tests"""
    print("\n" + "=" * 60)
    print("SUITE DE TESTS - MODÈLE DE GESTION DE CARBURANT")
    print("=" * 60)
    
    tests = [
        ("Cas simple", test_simple_case),
        ("Capacités serrées", test_capacity_constraint),
        ("Demande saisonnière", test_seasonal_demand),
        ("Performance", test_performance)
    ]
    
    results = []
    for name, test_func in tests:
        try:
            success = test_func()
            results.append((name, success))
        except Exception as e:
            print(f"\n❌ Erreur dans {name}: {str(e)}")
            results.append((name, False))
    
    # Résumé
    print("\n" + "=" * 60)
    print("RÉSUMÉ DES TESTS")
    print("=" * 60)
    for name, success in results:
        status = "✅ RÉUSSI" if success else "❌ ÉCHOUÉ"
        print(f"{name}: {status}")
    
    total = len(results)
    passed = sum(1 for _, s in results if s)
    print(f"\nTotal: {passed}/{total} tests réussis ({passed*100//total}%)")

if __name__ == '__main__':
    # Vérifier que Gurobi est installé
    try:
        import gurobipy as gp
        print("✅ Gurobi détecté")
    except ImportError:
        print("❌ Gurobi n'est pas installé!")
        print("Installez-le avec: pip install gurobipy")
        exit(1)
    
    # Exécuter les tests
    run_all_tests()