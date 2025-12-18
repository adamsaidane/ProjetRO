# Guide de Rédaction du Rapport
## Projet RO - Ordonnancement Multi-Période

---

## 📋 Structure Recommandée

### 1. Page de Garde (1 page)
**Éléments à inclure:**
- Logo INSAT
- Titre du projet complet
- Sous-titre: "Ordonnancement Multi-Période: Gestion des Stocks de Carburant pour Centrales Électriques"
- Noms des 5 membres avec photos d'identité
- Département et année universitaire
- Date de remise

**Conseil:** Utilisez LaTeX ou Word avec un template professionnel

---

### 2. Table des Matières (1 page)

---

### 3. Introduction (2-3 pages)

#### 3.1 Contexte
Expliquez le problème réel:
- Importance de la gestion énergétique
- Enjeux économiques de l'approvisionnement en carburant
- Variabilité des prix et de la demande
- Impact sur la production électrique

#### 3.2 Problématique
Décrivez le problème spécifique:
- Décisions à prendre (quand acheter, combien, auprès de qui)
- Contraintes à respecter (capacités, demandes, stocks)
- Objectif d'optimisation (minimisation des coûts)

#### 3.3 Objectifs du Projet
Listez les objectifs:
- Modéliser mathématiquement le problème
- Développer une application informatique
- Visualiser et interpréter les résultats
- Analyser différents scénarios

**Astuce:** Ajoutez un schéma illustrant le flux de carburant (fournisseurs → stock → centrales)

---

### 4. État de l'Art (1-2 pages)

Recherchez et citez:
- Articles sur la gestion de stocks multi-période
- Applications dans le secteur énergétique
- Techniques de programmation linéaire mixte
- Travaux similaires

**Ressources:**
- Google Scholar: "multi-period inventory management"
- ResearchGate: "fuel management power plants"
- Papers sur la PLM en énergie

---

### 5. Modélisation Mathématique (4-5 pages)

#### 5.1 Notations
Tableau récapitulatif de TOUS les indices, paramètres et variables

#### 5.2 Variables de Décision
Pour chaque variable, expliquez:
- Sa signification
- Son domaine (continu/binaire)
- Son rôle dans le modèle

**Exemple:**
```
x[t,s] ∈ ℝ⁺ : Quantité de carburant (en tonnes) achetée 
              au fournisseur s durant la période t
```

#### 5.3 Fonction Objectif
- Formulation mathématique complète
- Explication de chaque terme
- Justification de l'actualisation

**Conseil:** Décomposez la fonction en plusieurs parties:
```
Z = Z_achat + Z_fixe + Z_stockage + Z_penurie

où:
Z_achat = Σ[t,s] (1/(1+r)^t) × p[t,s] × x[t,s]
...
```

#### 5.4 Contraintes
Pour chaque contrainte:
1. Formulation mathématique
2. Explication en français
3. Justification (pourquoi est-elle nécessaire?)

**Exemple de présentation:**

**Contrainte 1: Conservation des stocks**
```
y[t-1] + Σ[s] x[t,s] - Σ[c] z[t,c] = y[t]  ∀t ≥ 1
```
Cette contrainte assure que le stock à la fin de la période t est égal au stock de la période précédente, plus les achats, moins les consommations. C'est l'équation de conservation de la masse.

#### 5.5 Classification du Problème
- Type: PLM (Programmation Linéaire Mixte)
- Complexité: NP-difficile
- Justification de la complexité

---

### 6. Architecture de l'Application (3-4 pages)

#### 6.1 Technologies Choisies
Pour chaque technologie, justifiez le choix:

**Python:**
- Langage de haut niveau
- Riche écosystème scientifique
- Intégration facile avec Gurobi

**PySide6:**
- Interface native et performante
- Gestion événementielle robuste
- Multithreading intégré

**Gurobi:**
- Solveur de référence en PLM
- Performances excellentes
- Licence académique gratuite

#### 6.2 Structure du Code
Diagramme de classes:
```
┌─────────────┐      utilise     ┌──────────────────┐
│  MainWindow │ ──────────────> │ FuelManagement   │
│             │                  │     Model        │
└─────────────┘                  └──────────────────┘
      │                                   │
      │ crée                              │ utilise
      ↓                                   ↓
┌─────────────┐                  ┌──────────────────┐
│ Optimization│                  │  gurobipy        │
│   Worker    │                  │   (Gurobi)       │
└─────────────┘                  └──────────────────┘
```

#### 6.3 Description des Modules
Pour chaque fichier Python:
- Rôle principal
- Classes/fonctions principales
- Interactions avec les autres modules

#### 6.4 Interface Utilisateur
Screenshots de chaque onglet avec annotations:
- Capture d'écran
- Légende expliquant les éléments
- Workflow utilisateur

**Conseil:** Utilisez des flèches et du texte pour annoter vos captures

---

### 7. Implémentation (3-4 pages)

#### 7.1 Modélisation avec Gurobi
Extraits de code commentés:

```python
# Fonction objectif
cout_total = gp.QuadExpr()
for t in range(T):
    # Facteur d'actualisation
    facteur = 1 / ((1 + r) ** t)
    
    # Coûts d'achat
    for s in range(S):
        cout_total += facteur * prix[t,s] * x[t,s]
```

**Conseil:** N'incluez pas tout le code, seulement les parties clés

#### 7.2 Gestion du Multithreading
Expliquez comment vous avez évité le blocage de l'interface:
- Utilisation de QThread
- Signaux Qt pour la communication
- Barre de progression

#### 7.3 Visualisation des Résultats
Expliquez les choix de visualisation:
- Graphique en ligne pour l'évolution du stock (tendance temporelle)
- Graphique en barres empilées pour les achats (comparaison)
- Etc.

---

### 8. Résultats et Analyse (5-6 pages)

#### 8.1 Scénario Principal
Décrivez en détail:
- Paramètres utilisés (tableau)
- Résultats obtenus (coût optimal, solution)
- Interprétation managériale

**Tableau des résultats:**
| Indicateur | Valeur |
|------------|--------|
| Coût total optimal | XXX,XXX € |
| Coût d'achat | XXX,XXX € |
| Coût de stockage | XX,XXX € |
| Coût fixe | XX,XXX € |
| Temps de résolution | X.XX s |

#### 8.2 Visualisations
Incluez au moins 4 graphiques:
1. **Évolution du stock**: Montrez comment le stock varie
2. **Achats par fournisseur**: Qui est privilégié et quand
3. **Consommation par centrale**: Distribution de la demande
4. **Répartition des coûts**: Camembert des différents coûts

**Pour chaque graphique:**
- Titre clair
- Axes bien légendés
- Commentaire d'interprétation

#### 8.3 Interprétation des Résultats

**Questions à répondre:**
- Quelle est la stratégie d'approvisionnement optimale?
- Quels fournisseurs sont les plus utilisés?
- Comment le stock évolue-t-il au cours du temps?
- Y a-t-il des périodes critiques?
- Les contraintes sont-elles saturées?

**Analyse économique:**
- Décomposition du coût total
- Identification des postes les plus importants
- Recommandations managériales

#### 8.4 Analyse de Sensibilité

Testez plusieurs scénarios:

**Variation du taux d'actualisation:**
| Taux | Coût Total | Variation |
|------|------------|-----------|
| 0% | XXX,XXX € | - |
| 3% | XXX,XXX € | +X% |
| 5% | XXX,XXX € | +X% |
| 10% | XXX,XXX € | +X% |

**Interprétation:** Plus le taux est élevé, plus...

**Variation de la capacité de stockage:**
- Graphique: Coût total vs Capacité
- Identification du point optimal

**Variation de la demande:**
- Impact d'une augmentation de 20% de la demande
- Identification des goulots d'étranglement

#### 8.5 Cas Limites
Testez des scénarios extrêmes:
- Capacités très serrées
- Demande très élevée
- Prix très volatils
- Rupture d'un fournisseur

---

### 9. Tests et Validation (2-3 pages)

#### 9.1 Stratégie de Test
- Tests unitaires (vérification du modèle)
- Tests d'intégration (interface + modèle)
- Tests de non-régression

#### 9.2 Validation des Résultats
Comment avez-vous validé?
- Vérification manuelle sur cas simple
- Comparaison avec solution heuristique
- Vérification de la cohérence des contraintes

#### 9.3 Gestion des Erreurs
- Cas d'infaisabilité
- Erreurs de saisie utilisateur
- Problèmes de licence Gurobi

---

### 10. Difficultés Rencontrées (1-2 pages)

Soyez honnêtes sur les difficultés:

**Exemple:**
- **Difficulté:** Choix du paramètre Big M
- **Solution:** Tests empiriques pour trouver une valeur appropriée
- **Leçon apprise:** L'importance de la normalisation des données

---

### 11. Conclusion (2 pages)

#### 11.1 Synthèse
Résumé du travail effectué

#### 11.2 Apports du Projet
Ce que vous avez appris:
- Connaissances techniques
- Compétences en modélisation
- Travail en équipe
- Gestion de projet

#### 11.3 Extensions Possibles
Améliorations futures:
- **Court terme:** Export Excel, sauvegarde de scénarios
- **Moyen terme:** Optimisation stochastique, multi-objectifs
- **Long terme:** Dashboard web, intégration IoT

#### 11.4 Perspectives
Applications possibles dans d'autres domaines:
- Gestion de stocks industriels
- Logistique de distribution
- Planification de production

---

### 12. Bibliographie (1 page)

**Format IEEE recommandé:**

[1] H.P. Williams, "Model Building in Mathematical Programming," 5th ed., Wiley, 2013.

[2] Gurobi Optimization, "Gurobi Optimizer Reference Manual," 2024. [Online]. Available: https://www.gurobi.com/documentation/

[3] A. Author, "Title of Paper," Journal Name, vol. X, no. Y, pp. Z-W, Year.

---

### 13. Annexes

#### Annexe A: Code Source Principal
Extraits des parties les plus importantes

#### Annexe B: Manuel Utilisateur
Guide pas-à-pas pour utiliser l'application

#### Annexe C: Captures d'Écran Supplémentaires
Toutes les vues de l'interface

#### Annexe D: Données de Test
Tableaux des données utilisées

---

## 🎨 Conseils de Présentation

### Mise en Page
- **Police:** Arial ou Times, 11-12pt
- **Interligne:** 1.15 ou 1.5
- **Marges:** 2.5cm de chaque côté
- **Numérotation:** Pages numérotées en bas à droite

### Figures et Tableaux
- **Toujours légendés** (Figure X: ..., Tableau Y: ...)
- **Référencés dans le texte** ("comme le montre la Figure 3...")
- **Haute résolution** (300 DPI minimum)
- **Légende sous les figures**, au-dessus des tableaux

### Code
- **Police monospace** (Courier, Consolas)
- **Coloration syntaxique** si possible
- **Commentaires en français**
- **Indentation propre**

### Équations
- **Numérotées** si référencées plus tard
- **Centrées**
- **Variables en italique**, opérateurs en romain
- **Explication après chaque équation**

---

## ⏱️ Planning de Rédaction

### Semaine 1
- [ ] Structure du document
- [ ] Introduction
- [ ] Modélisation mathématique

### Semaine 2
- [ ] Architecture et implémentation
- [ ] Captures d'écran
- [ ] Premiers résultats

### Semaine 3
- [ ] Analyse complète des résultats
- [ ] Graphiques et tableaux
- [ ] Tests et validation

### Semaine 4
- [ ] Conclusion
- [ ] Relecture et corrections
- [ ] Mise en page finale
- [ ] Génération PDF

---

## ✅ Checklist Finale

Avant de rendre:

### Contenu
- [ ] Toutes les sections sont complètes
- [ ] Figures et tableaux légendés et référencés
- [ ] Équations numérotées
- [ ] Bibliographie complète
- [ ] Code source en annexe

### Forme
- [ ] Orthographe vérifiée (Antidote, correcteur)
- [ ] Mise en page uniforme
- [ ] Page de garde professionnelle
- [ ] Table des matières à jour
- [ ] Numérotation des pages correcte

### Photos des Membres
- [ ] 5 photos d'identité de bonne qualité
- [ ] Noms et prénoms corrects
- [ ] Emails INSAT (@insat.rnu.tn)

### Livrable
- [ ] Fichier PDF nommé: Groupe_X_ProjetRO_2025.pdf
- [ ] Taille raisonnable (< 20 MB)
- [ ] Lisible et imprimable

---

## 🎯 Critères d'Évaluation à Viser

### Modélisation (30%)
- ✅ Complexité élevée (variables mixtes)
- ✅ Nombreuses contraintes réalistes
- ✅ Actualisation financière
- ✅ Gestion des pénuries

### IHM (20%)
- ✅ Interface intuitive et complète
- ✅ Multithreading fonctionnel
- ✅ Visualisations pertinentes
- ✅ Ergonomie professionnelle

### Résolution (20%)
- ✅ Utilisation correcte de Gurobi
- ✅ Résultats cohérents
- ✅ Performance acceptable
- ✅ Gestion des erreurs

### Rapport (20%)
- ✅ Structure claire
- ✅ Explications détaillées
- ✅ Analyse approfondie
- ✅ Présentation soignée

### Présentation (10%)
- ✅ Démonstration en direct
- ✅ Réponses aux questions
- ✅ Maîtrise du sujet
- ✅ Travail d'équipe visible

---

## 💡 Astuces pour Maximiser la Note

### 1. Complexité de la Modélisation
Votre modèle est déjà complexe, insistez sur:
- Variables continues ET binaires (PLM)
- Contraintes Big M
- Actualisation financière
- Multi-dimension (temps × fournisseurs × centrales)

### 2. Paramètres Nombreux
Comptez et mettez en avant:
- 12 périodes × 3 fournisseurs × 4 centrales = 144 prix d'achat
- 36 variables binaires de commande
- Plus de 200 variables de décision au total
- 60+ contraintes

### 3. Contraintes Réalistes
Expliquez pourquoi chaque contrainte:
- Reflète une limitation réelle
- Est nécessaire pour la validité du modèle
- Complexifie le problème

### 4. Analyse Approfondie
Ne vous contentez pas de présenter les résultats:
- Interprétez économiquement
- Faites des recommandations
- Analysez la sensibilité
- Discutez des limites

### 5. Extensions
Proposez des améliorations crédibles:
- Optimisation stochastique (incertitude sur demande/prix)
- Multi-objectifs (coût + émissions CO₂)
- Contraintes de robustesse
- Intégration de prévisions

---

## 📞 Ressources Utiles

### LaTeX
- Overleaf: https://www.overleaf.com (éditeur en ligne)
- Template rapport: https://www.latextemplates.com

### Bibliographie
- Google Scholar: https://scholar.google.com
- ResearchGate: https://www.researchgate.net
- Zotero (gestion de références): https://www.zotero.org

### Graphiques
- Matplotlib gallery: https://matplotlib.org/stable/gallery/
- Seaborn: Pour des graphiques plus esthétiques
- PlotLy: Pour des graphiques interactifs

---

## 🚀 Derniers Conseils

1. **Commencez tôt** - Ne laissez pas tout pour la dernière minute
2. **Répartissez le travail** - Chaque membre prend une section
3. **Faites des revues croisées** - Relisez le travail des autres
4. **Testez votre code** - Vérifiez que tout fonctionne avant de rendre
5. **Préparez la présentation** - Entraînez-vous à présenter ensemble

**Bon courage pour votre projet! Vous avez tous les outils pour réussir! 🎓✨**