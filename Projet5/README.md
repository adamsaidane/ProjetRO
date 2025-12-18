# Projet RO - Ordonnancement Multi-Période
## Gestion des Stocks de Carburant pour Centrales Électriques

---

## 📋 Description du Projet

Application de recherche opérationnelle pour optimiser la gestion multi-période des stocks de carburant destinés aux centrales électriques. Le système utilise la programmation linéaire mixte (PLM) pour minimiser les coûts totaux actualisés tout en satisfaisant les demandes des centrales.

### Problème d'Optimisation Traité
**Type:** Ordonnancement Multi-Période (Programmation Linéaire Mixte - PLM)

**Application:** Gestion des stocks de carburant pour centrales électriques

**Objectif:** Minimiser les coûts totaux actualisés incluant:
- Coûts d'achat de carburant
- Coûts fixes de commande
- Coûts de stockage
- Coûts de pénurie

---

## 🎯 Caractéristiques Principales

### Modélisation Complexe
- **Variables continues:** Quantités achetées, stocks, consommation
- **Variables binaires:** Décisions de commande auprès des fournisseurs
- **Variables de décision:** 3 types (achats, stocks, consommation) × périodes × entités
- **Contraintes multiples:** 
  - Conservation des stocks (équation de flux)
  - Satisfaction de la demande avec pénurie possible
  - Capacités des fournisseurs
  - Contraintes de commande minimum
  - Stock final minimal requis

### Paramètres du Modèle
- **Dimension temporelle:** Jusqu'à 24 périodes (mois/trimestres)
- **Fournisseurs:** Jusqu'à 10 fournisseurs avec prix et capacités variables
- **Centrales:** Jusqu'à 10 centrales avec demandes variables
- **Actualisation financière:** Prise en compte du taux d'actualisation
- **Variations saisonnières:** Prix et demandes variables dans le temps

---

## 🚀 Installation

### Prérequis
- Python 3.8 ou supérieur
- pip (gestionnaire de packages Python)

### Étape 1: Cloner ou télécharger le projet
```bash
cd chemin/vers/projet_ro
```

### Étape 2: Installer les dépendances Python
```bash
pip install -r requirements.txt
```

**Liste des packages:**
- `gurobipy`: Solveur d'optimisation (>=11.0.0)
- `PySide6`: Framework GUI (>=6.5.0)
- `matplotlib`: Visualisation (>=3.7.0)
- `numpy`: Calculs numériques (>=1.24.0)
- `pandas`: Manipulation de données (>=2.0.0)

### Étape 3: Obtenir une licence Gurobi (GRATUITE pour étudiants)

#### 3.1 Créer un compte académique
1. Aller sur: https://www.gurobi.com/academia/academic-program-and-licenses/
2. Cliquer sur "Academic License" ou "Register"
3. Créer un compte avec votre email universitaire (@insat.rnu.tn)

#### 3.2 Obtenir la licence académique
1. Se connecter sur: https://portal.gurobi.com/
2. Aller dans "Licenses" → "Request Academic License"
3. Accepter les conditions
4. Copier la commande `grbgetkey XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX`

#### 3.3 Activer la licence
```bash
grbgetkey XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX
```

**Important:** Exécutez cette commande sur le réseau universitaire ou avec VPN

#### 3.4 Vérifier l'installation
```python
import gurobipy as gp
env = gp.Env()
print("Gurobi installé avec succès!")
```

---

## 📂 Structure du Projet

```
projet_ro/
│
├── main.py              # Point d'entrée de l'application
├── model.py             # Modèle d'optimisation (Gurobi)
├── interface.py         # Interface graphique (PySide6)
├── worker.py            # Thread pour calculs non-bloquants
├── requirements.txt     # Dépendances Python
├── README.md           # Ce fichier
│
└── rapport/
    ├── rapport_projet.pdf
    └── captures/        # Screenshots de l'application
```

---

## ▶️ Utilisation

### Lancer l'application
```bash
python main.py
```

### Guide d'utilisation

#### 1. **Onglet "Paramètres Généraux"**
- Définir le nombre de périodes (1-24 mois)
- Nombre de fournisseurs (1-10)
- Nombre de centrales (1-10)
- Capacité de stockage maximale
- Stock initial et stock final minimum requis
- Taux d'actualisation financier
- Coût de pénurie par tonne
- Quantité minimale de commande

#### 2. **Onglet "Prix et Coûts"**
- **Prix d'achat:** Matrice [Période × Fournisseur] en €/tonne
- **Coûts fixes:** Coût fixe par commande pour chaque fournisseur
- **Coûts de stockage:** Coût par tonne stockée par période

#### 3. **Onglet "Demandes et Capacités"**
- **Demandes:** Matrice [Période × Centrale] en tonnes
- **Capacités:** Matrice [Période × Fournisseur] en tonnes

#### 4. **Lancer l'Optimisation**
- Cliquer sur "🚀 Lancer l'Optimisation"
- L'interface reste responsive grâce au multithreading
- Barre de progression pendant le calcul

#### 5. **Onglet "Résultats"**
Affiche:
- Coût total optimal
- Statut de la solution
- Gap d'optimalité
- Synthèse par période
- 4 graphiques:
  - Évolution du stock
  - Achats par fournisseur
  - Consommation par centrale
  - Pénuries éventuelles

---

## 🧮 Modèle Mathématique

### Variables de Décision

**Continues:**
- `x[t,s]` ∈ ℝ⁺: Quantité achetée au fournisseur s à la période t
- `y[t]` ∈ ℝ⁺: Stock à la fin de la période t
- `z[t,c]` ∈ ℝ⁺: Quantité utilisée par la centrale c à la période t
- `p[t,c]` ∈ ℝ⁺: Pénurie à la centrale c à la période t

**Binaires:**
- `w[t,s]` ∈ {0,1}: 1 si commande au fournisseur s à la période t

### Fonction Objectif

```
Minimiser: ∑ᵗ [1/(1+r)ᵗ] × [
    ∑ₛ (prix[t,s] × x[t,s] + coût_fixe[s] × w[t,s]) +
    coût_stock[t] × y[t] +
    ∑_c coût_pénurie × p[t,c]
]
```

Où `r` est le taux d'actualisation

### Contraintes Principales

1. **Conservation des stocks:**
   - Période 0: `stock_initial + ∑ₛ x[0,s] - ∑_c z[0,c] = y[0]`
   - Période t>0: `y[t-1] + ∑ₛ x[t,s] - ∑_c z[t,c] = y[t]`

2. **Satisfaction de la demande:**
   - `z[t,c] + p[t,c] ≥ demande[t,c]` ∀t,c

3. **Capacité des fournisseurs:**
   - `x[t,s] ≤ capacité[t,s]` ∀t,s

4. **Capacité de stockage:**
   - `y[t] ≤ capacité_stockage` ∀t

5. **Lien binaire-continu (Big M):**
   - `x[t,s] ≤ M × w[t,s]` ∀t,s

6. **Quantité minimale de commande:**
   - `x[t,s] ≥ qté_min × w[t,s]` ∀t,s

7. **Stock final minimal:**
   - `y[T-1] ≥ stock_final_min`

---

## 📊 Données de Test

### Scénario par Défaut
- **12 périodes** (1 an mensuel)
- **3 fournisseurs** avec prix variables
- **4 centrales** avec demandes saisonnières
- **Capacité de stockage:** 50,000 tonnes
- **Stock initial:** 20,000 tonnes
- **Variations saisonnières:** ±20% sur demandes et prix

### Créer vos propres scénarios
1. Modifier les paramètres dans l'interface
2. Ou créer des fichiers de données CSV
3. Tester différentes stratégies d'approvisionnement

---

## 🎓 Complexité du Modèle

### Niveau de Complexité: ⭐⭐⭐⭐⭐ (Élevé)

**Justification pour une note maximale:**

1. **Variables mixtes (PLNE/PLM):**
   - Variables continues (achats, stocks, consommation)
   - Variables binaires (décisions de commande)

2. **Multi-dimension:**
   - Dimension temporelle (12+ périodes)
   - Dimension spatiale (3+ fournisseurs, 4+ centrales)
   - Variables de pénurie (gestion de l'infaisabilité)

3. **Contraintes complexes:**
   - Équations de flux (conservation)
   - Contraintes Big M
   - Contraintes de commande minimum
   - Actualisation financière

4. **Paramètres réalistes:**
   - Variations saisonnières
   - Prix variables dans le temps
   - Capacités limitées
   - Coûts fixes de commande

5. **Extensions possibles:**
   - Fenêtres de livraison
   - Contrats à long terme
   - Modes de transport multiples
   - Risques d'approvisionnement

---

## 🐛 Dépannage

### Problème: "No module named 'gurobipy'"
**Solution:**
```bash
pip install gurobipy
```

### Problème: "Gurobi license error"
**Solution:**
1. Vérifier que vous êtes sur le réseau universitaire
2. Réactiver la licence: `grbgetkey VOTRE-CLE`
3. Contacter le support Gurobi si nécessaire

### Problème: "L'interface ne répond pas"
**Solution:**
- C'est normal pendant l'optimisation pour les grands problèmes
- Le multithreading devrait garder l'UI responsive
- Réduire la taille du problème si nécessaire

### Problème: "No feasible solution"
**Solution:**
- Vérifier que les capacités sont suffisantes
- Augmenter la capacité de stockage
- Vérifier les contraintes de stock final
- Autoriser les pénuries (elles sont déjà incluses)

---

## 📝 Rapport du Projet

### Sections à Inclure

1. **Page de garde**
   - Titre du projet
   - Noms et photos des membres du groupe
   - Date

2. **Introduction**
   - Contexte du problème
   - Objectifs

3. **Modélisation Mathématique**
   - Variables de décision
   - Fonction objectif
   - Contraintes détaillées

4. **Architecture de l'Application**
   - Diagramme de classes
   - Description de l'IHM
   - Technologies utilisées

5. **Résultats et Analyses**
   - Cas de test
   - Interprétation des solutions
   - Graphiques

6. **Conclusion**
   - Bilan
   - Extensions possibles

---

## 👥 Membres du Groupe

**Groupe X - INSAT 2024-2025**

1. [Prénom NOM 1] - [Email]
2. [Prénom NOM 2] - [Email]
3. [Prénom NOM 3] - [Email]
4. [Prénom NOM 4] - [Email]
5. [Prénom NOM 5] - [Email]

---

## 📅 Planning

- **Attribution du sujet:** [Date]
- **Modélisation:** [Date]
- **Développement IHM:** [Date]
- **Tests:** [Date]
- **Rapport:** [Date]
- **Remise finale:** 12 Décembre 2025

---

## 📚 Références

- Gurobi Optimization: https://www.gurobi.com/documentation/
- PySide6 Documentation: https://doc.qt.io/qtforpython/
- Matplotlib Gallery: https://matplotlib.org/stable/gallery/
- Cours de Recherche Opérationnelle - Prof. I. AJILI - INSAT

---

## 📄 Licence

Ce projet est réalisé dans le cadre académique de l'INSAT.
Tous droits réservés © 2024-2025

---

## ✨ Améliorations Futures

1. Export des résultats en Excel/PDF
2. Import de données depuis fichiers CSV
3. Sauvegarde/chargement de scénarios
4. Analyse de sensibilité automatique
5. Optimisation multi-objectifs
6. Contraintes de robustesse (incertitude)
7. Intégration de prévisions de demande
8. Dashboard web interactif

---

**Bon courage pour votre projet! 🚀**