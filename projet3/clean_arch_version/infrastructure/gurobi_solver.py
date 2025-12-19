from typing import List, Tuple
import gurobipy as gp
from gurobipy import GRB

from ..domain.model import TelecomInstance, Solution
from ..domain.ports import ISolver

class GurobiTelecomSolver(ISolver):
    def solve(self, instance: TelecomInstance, edges: List[Tuple[int, int]]) -> Solution:
        n = len(instance.nodes)
        if n == 0:
            return Solution([], 0.0, 0.0, 0)

        m = gp.Model("Telecom_WIS_Budget")
        m.setParam("OutputFlag", 0)

        x = m.addVars(n, vtype=GRB.BINARY, name="x")

        # Objective: max sum(w_i * x_i)
        m.setObjective(gp.quicksum(instance.nodes[i].w * x[i] for i in range(n)), GRB.MAXIMIZE)

        # Conflicts: x_i + x_j <= 1
        m.addConstrs((x[i] + x[j] <= 1 for (i, j) in edges), name="no_interference")

        # Budget: sum(c_i * x_i) <= B
        m.addConstr(gp.quicksum(instance.nodes[i].c * x[i] for i in range(n)) <= instance.B, name="budget")

        m.optimize()

        if m.Status != GRB.OPTIMAL:
            return Solution([], 0.0, 0.0, len(edges))

        selected = [i for i in range(n) if x[i].X > 0.5]
        total_w = sum(instance.nodes[i].w for i in selected)
        total_c = sum(instance.nodes[i].c for i in selected)

        m.dispose()
        return Solution(selected, total_w, total_c, len(edges))
