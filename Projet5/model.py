"""
Modèle d'optimisation pour l'ordonnancement multi-période
Gestion des stocks de carburant pour centrales électriques
"""

import gurobipy as gp
from gurobipy import GRB
import numpy as np

class FuelManagementModel:
    """
    Modèle de programmation linéaire mixte pour la gestion des stocks de carburant
    
    Variables de décision:
    - x[t,s]: Quantité de carburant du fournisseur s achetée à la période t
    - y[t]: Quantité stockée à la fin de la période t
    - z[t,c]: Quantité de carburant utilisée par la centrale c à la période t
    - w[t,s]: Variable binaire (1 si achat au fournisseur s à la période t, 0 sinon)
    """
    
    def __init__(self):
        self.model = None
        self.x = None  # Quantités achetées
        self.y = None  # Stock
        self.z = None  # Consommation
        self.w = None  # Variables binaires d'achat
        
    def build_model(self, data):
        """
        Construit le modèle d'optimisation
        
        Args:
            data: Dictionnaire contenant tous les paramètres
        """
        # Extraire les données
        T = data['nb_periodes']
        S = data['nb_fournisseurs']
        C = data['nb_centrales']
        
        # Coûts et paramètres
        prix_achat = np.array(data['prix_achat'])  # [t,s]
        cout_stock = np.array(data['cout_stockage'])  # [t]
        cout_fixe = np.array(data['cout_fixe_commande'])  # [s]
        demande = np.array(data['demande_centrales'])  # [t,c]
        capacite_stock = data['capacite_stockage']
        stock_initial = data['stock_initial']
        stock_final_min = data['stock_final_min']
        capacite_fournisseur = np.array(data['capacite_fournisseur'])  # [t,s]
        cout_penurie = data['cout_penurie']
        taux_actualisation = data['taux_actualisation']
        
        # Créer le modèle
        self.model = gp.Model("GestionCarburantCentrales")
        self.model.setParam('OutputFlag', 0)  # Désactiver sortie console
        
        # Variables de décision
        # x[t,s]: Quantité achetée au fournisseur s à la période t
        self.x = self.model.addVars(T, S, lb=0, name="Achat")
        
        # y[t]: Stock à la fin de la période t
        self.y = self.model.addVars(T, lb=0, ub=capacite_stock, name="Stock")
        
        # z[t,c]: Quantité utilisée par la centrale c à la période t
        self.z = self.model.addVars(T, C, lb=0, name="Consommation")
        
        # w[t,s]: Variable binaire (1 si achat au fournisseur s à la période t)
        self.w = self.model.addVars(T, S, vtype=GRB.BINARY, name="CommandeFournisseur")
        
        # p[t,c]: Pénurie à la centrale c à la période t
        self.p = self.model.addVars(T, C, lb=0, name="Penurie")
        
        # Fonction objectif: Minimiser les coûts totaux actualisés
        cout_total = gp.QuadExpr()
        
        for t in range(T):
            facteur_actualisation = 1 / ((1 + taux_actualisation) ** t)
            
            # Coûts d'achat
            for s in range(S):
                cout_total += facteur_actualisation * prix_achat[t,s] * self.x[t,s]
                # Coût fixe si commande
                cout_total += facteur_actualisation * cout_fixe[s] * self.w[t,s]
            
            # Coûts de stockage
            cout_total += facteur_actualisation * cout_stock[t] * self.y[t]
            
            # Coûts de pénurie
            for c in range(C):
                cout_total += facteur_actualisation * cout_penurie * self.p[t,c]
        
        self.model.setObjective(cout_total, GRB.MINIMIZE)
        
        # CONTRAINTES
        
        # 1. Équilibre des stocks (conservation de la masse)
        for t in range(T):
            if t == 0:
                # Première période
                self.model.addConstr(
                    stock_initial + gp.quicksum(self.x[t,s] for s in range(S)) - 
                    gp.quicksum(self.z[t,c] for c in range(C)) == self.y[t],
                    name=f"Equilibre_Stock_t{t}"
                )
            else:
                # Périodes suivantes
                self.model.addConstr(
                    self.y[t-1] + gp.quicksum(self.x[t,s] for s in range(S)) - 
                    gp.quicksum(self.z[t,c] for c in range(C)) == self.y[t],
                    name=f"Equilibre_Stock_t{t}"
                )
        
        # 2. Satisfaction de la demande (avec pénurie possible)
        for t in range(T):
            for c in range(C):
                self.model.addConstr(
                    self.z[t,c] + self.p[t,c] >= demande[t,c],
                    name=f"Demande_t{t}_c{c}"
                )
        
        # 3. Capacité des fournisseurs
        for t in range(T):
            for s in range(S):
                self.model.addConstr(
                    self.x[t,s] <= capacite_fournisseur[t,s],
                    name=f"Capacite_Fournisseur_t{t}_s{s}"
                )
        
        # 4. Lien entre variable binaire et quantité achetée (Big M)
        M = 1e6  # Big M
        for t in range(T):
            for s in range(S):
                self.model.addConstr(
                    self.x[t,s] <= M * self.w[t,s],
                    name=f"Lien_Binaire_t{t}_s{s}"
                )
        
        # 5. Stock final minimal
        self.model.addConstr(
            self.y[T-1] >= stock_final_min,
            name="Stock_Final_Min"
        )
        
        # 6. Contraintes de quantité minimale de commande
        if 'qte_min_commande' in data:
            qte_min = data['qte_min_commande']
            for t in range(T):
                for s in range(S):
                    self.model.addConstr(
                        self.x[t,s] >= qte_min * self.w[t,s],
                        name=f"Qte_Min_Commande_t{t}_s{s}"
                    )
        
    def optimize(self):
        """Résout le modèle d'optimisation"""
        if self.model is None:
            raise ValueError("Le modèle n'a pas été construit")
        
        self.model.optimize()
        
        if self.model.status == GRB.OPTIMAL:
            return True
        else:
            return False
    
    def get_results(self):
        """Extrait les résultats de l'optimisation"""
        if self.model.status != GRB.OPTIMAL:
            return None
        
        results = {
            'cout_optimal': self.model.objVal,
            'status': 'Optimal',
            'gap': self.model.MIPGap if hasattr(self.model, 'MIPGap') else 0,
            'achats': {},
            'stocks': {},
            'consommation': {},
            'penuries': {},
            'commandes': {}
        }
        
        # Extraire les valeurs des variables
        for v in self.model.getVars():
            if v.varName.startswith('Achat'):
                results['achats'][v.varName] = v.x
            elif v.varName.startswith('Stock'):
                results['stocks'][v.varName] = v.x
            elif v.varName.startswith('Consommation'):
                results['consommation'][v.varName] = v.x
            elif v.varName.startswith('Penurie'):
                results['penuries'][v.varName] = v.x
            elif v.varName.startswith('CommandeFournisseur'):
                results['commandes'][v.varName] = v.x
        
        return results
    
    def get_solution_arrays(self, T, S, C):
        """Retourne les solutions sous forme de tableaux numpy"""
        achats = np.zeros((T, S))
        stocks = np.zeros(T)
        consommation = np.zeros((T, C))
        penuries = np.zeros((T, C))
        commandes = np.zeros((T, S))
        
        for t in range(T):
            for s in range(S):
                achats[t,s] = self.x[t,s].x
                commandes[t,s] = self.w[t,s].x
            stocks[t] = self.y[t].x
            for c in range(C):
                consommation[t,c] = self.z[t,c].x
                penuries[t,c] = self.p[t,c].x
        
        return achats, stocks, consommation, penuries, commandes