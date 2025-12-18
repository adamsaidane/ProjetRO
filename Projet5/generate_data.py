"""
Générateur de données réalistes pour le projet
Crée des scénarios de test variés
"""

import numpy as np
import pandas as pd
import json

class DataGenerator:
    """Génère des données réalistes pour différents scénarios"""
    
    @staticmethod
    def generate_base_scenario(T=12, S=3, C=4):
        """Génère un scénario de base avec variations saisonnières"""
        
        # Prix d'achat avec variations saisonnières (hiver plus cher)
        base_prices = [100, 95, 110]  # Prix de base par fournisseur
        prix_achat = np.zeros((T, S))
        for t in range(T):
            # Hiver (nov-fev): +20%, Été (mai-août): -10%
            month = t % 12
            if month in [10, 11, 0, 1]:  # Hiver
                seasonal_factor = 1.2
            elif month in [4, 5, 6, 7]:  # Été
                seasonal_factor = 0.9
            else:
                seasonal_factor = 1.0
            
            for s in range(S):
                # Ajouter un peu de randomness
                noise = np.random.uniform(-5, 5)
                prix_achat[t, s] = base_prices[s % 3] * seasonal_factor + noise
        
        # Coûts fixes de commande
        cout_fixe = np.array([5000, 4500, 5500] + [5000] * (S-3))[:S]
        
        # Coûts de stockage (constants)
        cout_stock = np.full(T, 2.5)
        
        # Demande avec variations saisonnières (hiver plus élevé)
        base_demands = [3000, 3500, 2800, 4000] + [3200] * (C-4)
        base_demands = base_demands[:C]
        demande = np.zeros((T, C))
        for t in range(T):
            month = t % 12
            if month in [10, 11, 0, 1, 2]:  # Hiver
                seasonal_factor = 1.3
            elif month in [5, 6, 7, 8]:  # Été
                seasonal_factor = 0.8
            else:
                seasonal_factor = 1.0
            
            for c in range(C):
                demande[t, c] = base_demands[c] * seasonal_factor
        
        # Capacités des fournisseurs
        capacite_fournisseur = np.zeros((T, S))
        base_capacities = [8000, 10000, 7000] + [8500] * (S-3)
        base_capacities = base_capacities[:S]
        for t in range(T):
            for s in range(S):
                # Petite variation de capacité
                variation = np.random.uniform(-500, 500)
                capacite_fournisseur[t, s] = base_capacities[s] + variation
        
        return {
            'nb_periodes': T,
            'nb_fournisseurs': S,
            'nb_centrales': C,
            'prix_achat': prix_achat,
            'cout_fixe_commande': cout_fixe,
            'cout_stockage': cout_stock,
            'demande_centrales': demande,
            'capacite_fournisseur': capacite_fournisseur,
            'capacite_stockage': 50000,
            'stock_initial': 20000,
            'stock_final_min': 15000,
            'taux_actualisation': 0.05,
            'cout_penurie': 500,
            'qte_min_commande': 1000
        }
    
    @staticmethod
    def generate_tight_capacity_scenario(T=12, S=3, C=4):
        """Génère un scénario avec capacités serrées"""
        data = DataGenerator.generate_base_scenario(T, S, C)
        
        # Réduire les capacités
        data['capacite_fournisseur'] *= 0.7
        data['capacite_stockage'] = 30000
        data['stock_initial'] = 15000
        
        return data
    
    @staticmethod
    def generate_price_volatility_scenario(T=12, S=3, C=4):
        """Génère un scénario avec forte volatilité des prix"""
        data = DataGenerator.generate_base_scenario(T, S, C)
        
        # Augmenter la volatilité des prix
        for t in range(T):
            for s in range(S):
                volatility = np.random.uniform(-20, 20)
                data['prix_achat'][t, s] += volatility
        
        return data
    
    @staticmethod
    def generate_demand_spike_scenario(T=12, S=3, C=4):
        """Génère un scénario avec pics de demande"""
        data = DataGenerator.generate_base_scenario(T, S, C)
        
        # Ajouter des pics de demande aléatoires
        spike_periods = np.random.choice(T, size=3, replace=False)
        for t in spike_periods:
            data['demande_centrales'][t] *= 1.5
        
        return data
    
    @staticmethod
    def save_to_csv(data, filename_prefix="scenario"):
        """Sauvegarde les données dans des fichiers CSV"""
        
        T = data['nb_periodes']
        S = data['nb_fournisseurs']
        C = data['nb_centrales']
        
        # Prix d'achat
        df_prix = pd.DataFrame(
            data['prix_achat'],
            columns=[f'Fournisseur_{s+1}' for s in range(S)],
            index=[f'Periode_{t+1}' for t in range(T)]
        )
        df_prix.to_csv(f'{filename_prefix}_prix_achat.csv')
        
        # Coûts fixes
        df_fixe = pd.DataFrame({
            'Fournisseur': [f'Fournisseur_{s+1}' for s in range(S)],
            'Cout_Fixe': data['cout_fixe_commande']
        })
        df_fixe.to_csv(f'{filename_prefix}_cout_fixe.csv', index=False)
        
        # Coûts de stockage
        df_stock = pd.DataFrame({
            'Periode': [f'Periode_{t+1}' for t in range(T)],
            'Cout_Stockage': data['cout_stockage']
        })
        df_stock.to_csv(f'{filename_prefix}_cout_stockage.csv', index=False)
        
        # Demande
        df_demande = pd.DataFrame(
            data['demande_centrales'],
            columns=[f'Centrale_{c+1}' for c in range(C)],
            index=[f'Periode_{t+1}' for t in range(T)]
        )
        df_demande.to_csv(f'{filename_prefix}_demande.csv')
        
        # Capacités
        df_capacite = pd.DataFrame(
            data['capacite_fournisseur'],
            columns=[f'Fournisseur_{s+1}' for s in range(S)],
            index=[f'Periode_{t+1}' for t in range(T)]
        )
        df_capacite.to_csv(f'{filename_prefix}_capacite_fournisseur.csv')
        
        # Paramètres généraux
        params = {
            'capacite_stockage': data['capacite_stockage'],
            'stock_initial': data['stock_initial'],
            'stock_final_min': data['stock_final_min'],
            'taux_actualisation': data['taux_actualisation'],
            'cout_penurie': data['cout_penurie'],
            'qte_min_commande': data['qte_min_commande']
        }
        with open(f'{filename_prefix}_parametres.json', 'w') as f:
            json.dump(params, f, indent=4)
        
        print(f"✅ Données sauvegardées: {filename_prefix}_*.csv")
    
    @staticmethod
    def print_scenario_summary(data):
        """Affiche un résumé du scénario"""
        T = data['nb_periodes']
        S = data['nb_fournisseurs']
        C = data['nb_centrales']
        
        print("\n" + "="*60)
        print("RÉSUMÉ DU SCÉNARIO")
        print("="*60)
        print(f"📅 Périodes: {T}")
        print(f"🏭 Fournisseurs: {S}")
        print(f"⚡ Centrales: {C}")
        print(f"\n💰 PRIX D'ACHAT:")
        print(f"  Min: {data['prix_achat'].min():.2f} €/tonne")
        print(f"  Max: {data['prix_achat'].max():.2f} €/tonne")
        print(f"  Moyenne: {data['prix_achat'].mean():.2f} €/tonne")
        print(f"\n📊 DEMANDE:")
        print(f"  Min par période: {data['demande_centrales'].sum(axis=1).min():.0f} tonnes")
        print(f"  Max par période: {data['demande_centrales'].sum(axis=1).max():.0f} tonnes")
        print(f"  Total: {data['demande_centrales'].sum():.0f} tonnes")
        print(f"\n🏗️ CAPACITÉS:")
        print(f"  Stockage: {data['capacite_stockage']:.0f} tonnes")
        print(f"  Fournisseurs (par période): {data['capacite_fournisseur'].sum(axis=1).mean():.0f} tonnes")
        print(f"\n💵 AUTRES PARAMÈTRES:")
        print(f"  Coût fixe moyen: {data['cout_fixe_commande'].mean():.0f} €")
        print(f"  Coût de stockage: {data['cout_stockage'][0]:.2f} €/tonne")
        print(f"  Coût de pénurie: {data['cout_penurie']:.0f} €/tonne")
        print(f"  Taux d'actualisation: {data['taux_actualisation']*100:.1f}%")
        print("="*60)

def main():
    """Génère plusieurs scénarios de test"""
    
    print("🎲 GÉNÉRATEUR DE DONNÉES - GESTION DE CARBURANT")
    print("="*60)
    
    scenarios = [
        ("scenario_base", "Scénario de base", 
         lambda: DataGenerator.generate_base_scenario(12, 3, 4)),
        
        ("scenario_capacite_serree", "Capacités serrées", 
         lambda: DataGenerator.generate_tight_capacity_scenario(12, 3, 4)),
        
        ("scenario_prix_volatil", "Prix volatils", 
         lambda: DataGenerator.generate_price_volatility_scenario(12, 3, 4)),
        
        ("scenario_pic_demande", "Pics de demande", 
         lambda: DataGenerator.generate_demand_spike_scenario(12, 3, 4)),
        
        ("scenario_annuel_large", "Scénario annuel (5 fournisseurs, 6 centrales)", 
         lambda: DataGenerator.generate_base_scenario(12, 5, 6)),
        
        ("scenario_bi_annuel", "Scénario bi-annuel (24 périodes)", 
         lambda: DataGenerator.generate_base_scenario(24, 3, 4)),
    ]
    
    for filename, description, generator_func in scenarios:
        print(f"\n🔄 Génération: {description}")
        data = generator_func()
        DataGenerator.print_scenario_summary(data)
        DataGenerator.save_to_csv(data, filename)
    
    print("\n" + "="*60)
    print("✅ Tous les scénarios ont été générés!")
    print("="*60)
    print("\nFichiers créés:")
    print("  - scenario_base_*.csv")
    print("  - scenario_capacite_serree_*.csv")
    print("  - scenario_prix_volatil_*.csv")
    print("  - scenario_pic_demande_*.csv")
    print("  - scenario_annuel_large_*.csv")
    print("  - scenario_bi_annuel_*.csv")
    print("\nUtilisez ces fichiers pour tester votre application!")

if __name__ == '__main__':
    main()