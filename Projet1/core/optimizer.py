import gurobipy as gp
from gurobipy import GRB
from Projet1.models.optimization_result import OptimizationResult


class ProcessAllocationOptimizer:
    # Poids de priorité pour la fonction objectif
    PRIORITY_WEIGHTS = {
        1: 2.0,  # Critique
        2: 1.5,  # Haute
        3: 1.0,  # Normale
        4: 0.5  # Basse
    }

    def __init__(self):
        self.processes = []
        self.config = None
        self.model = None
        self.variables = {}

    def add_process(self, process):
        self.processes.append(process)

    def set_processes(self, processes):
        self.processes = processes.copy()

    def set_configuration(self, config):
        self.config = config

    def build_model(self):
        if not self.processes:
            raise ValueError("Aucun processus défini")
        if not self.config:
            raise ValueError("Configuration système non définie")

        # Créer le modèle Gurobi
        self.model = gp.Model("ProcessAllocation")
        self.model.setParam('OutputFlag', 0)  # Désactiver les logs

        # Variables de décision (binaires)
        self.variables = {}
        for proc in self.processes:
            self.variables[proc.name] = self.model.addVar(
                vtype=GRB.BINARY,
                name=f"x_{proc.name}"
            )

        # Fonction objectif : Maximiser la valeur pondérée
        objective = gp.quicksum(
            proc.value * self.PRIORITY_WEIGHTS[proc.priority] * self.variables[proc.name]
            for proc in self.processes
        )
        self.model.setObjective(objective, GRB.MAXIMIZE)

        # ==================== CONTRAINTES ====================

        # 1. Contrainte CPU
        self.model.addConstr(
            gp.quicksum(proc.cpu * self.variables[proc.name]
                        for proc in self.processes) <= self.config.cpu_max,
            name="CPU_constraint"
        )

        # 2. Contrainte RAM
        self.model.addConstr(
            gp.quicksum(proc.ram * self.variables[proc.name]
                        for proc in self.processes) <= self.config.ram_max,
            name="RAM_constraint"
        )

        # 3. Contrainte Threads
        self.model.addConstr(
            gp.quicksum(proc.threads * self.variables[proc.name]
                        for proc in self.processes) <= self.config.threads_max,
            name="Threads_constraint"
        )

        # 4. Contrainte de temps (si spécifiée)
        if self.config.time_max is not None and self.config.time_max > 0:
            self.model.addConstr(
                gp.quicksum(proc.duration * self.variables[proc.name]
                            for proc in self.processes) <= self.config.time_max,
                name="Time_constraint"
            )

        # 5. Contrainte : Nombre minimum de processus critiques
        critical_processes = [p for p in self.processes if p.priority == 1]
        if self.config.min_critical > 0 and critical_processes:
            self.model.addConstr(
                gp.quicksum(self.variables[p.name] for p in critical_processes)
                >= self.config.min_critical,
                name="Min_critical_constraint"
            )

        # 6. Contrainte : Nombre maximum de processus basse priorité
        low_priority_processes = [p for p in self.processes if p.priority == 4]
        if self.config.max_low is not None and self.config.max_low > 0 and low_priority_processes:
            self.model.addConstr(
                gp.quicksum(self.variables[p.name] for p in low_priority_processes)
                <= self.config.max_low,
                name="Max_low_priority_constraint"
            )

        # 7. Contraintes de dépendances
        for proc in self.processes:
            for dep_name in proc.dependencies:
                if dep_name in self.variables:
                    self.model.addConstr(
                        self.variables[proc.name] <= self.variables[dep_name],
                        name=f"Dependency_{proc.name}_requires_{dep_name}"
                    )

        # 8. Contraintes d'incompatibilité
        for proc in self.processes:
            for incomp_name in proc.incompatible_with:
                if incomp_name in self.variables:
                    self.model.addConstr(
                        self.variables[proc.name] + self.variables[incomp_name] <= 1,
                        name=f"Incompatibility_{proc.name}_{incomp_name}"
                    )

    def optimize(self):
        if self.model is None:
            raise RuntimeError("Le modèle doit être construit avant l'optimisation")

        # Lancer l'optimisation
        self.model.optimize()

        # Analyser les résultats
        if self.model.status == GRB.OPTIMAL:
            selected_processes = []
            total_cpu = 0
            total_ram = 0
            total_threads = 0
            total_time = 0

            for proc in self.processes:
                if self.variables[proc.name].X > 0.5:  # Processus sélectionné
                    selected_processes.append(proc)
                    total_cpu += proc.cpu
                    total_ram += proc.ram
                    total_threads += proc.threads
                    total_time += proc.duration

            return OptimizationResult(
                status='Optimal',
                objective_value=self.model.ObjVal,
                selected_processes=selected_processes,
                total_cpu=total_cpu,
                total_ram=total_ram,
                total_threads=total_threads,
                total_time=total_time
            )

        elif self.model.status == GRB.INFEASIBLE:
            return OptimizationResult(status='Infaisable - Aucune solution trouvée')

        elif self.model.status == GRB.UNBOUNDED:
            return OptimizationResult(status='Non borné')

        else:
            return OptimizationResult(status=f'Statut inconnu: {self.model.status}')

    def solve(self, processes, config):
        self.set_processes(processes)
        self.set_configuration(config)
        self.build_model()
        return self.optimize()