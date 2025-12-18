import networkx as nx
import gurobipy as gp
from gurobipy import GRB
from typing import List, Dict, Set
from ..models.lesson import Lesson

def solve_mwis_gurobi(
    G: nx.Graph,
    lessons: List[Lesson],
    weights: Dict[Lesson, float] = None
) -> List[Lesson]:
    if weights is None:
        weights = {lesson: 1.0 for lesson in lessons}
    
    # Map lesson → index
    lesson_to_idx = {lesson: i for i, lesson in enumerate(lessons)}
    
    model = gp.Model("MWIS")
    model.setParam("OutputFlag", 0)

    x = model.addVars(len(lessons), vtype=GRB.BINARY, name="x")
    model.setObjective(
        gp.quicksum(weights[lessons[i]] * x[i] for i in range(len(lessons))),
        GRB.MAXIMIZE
    )

    for i, j in G.edges():
        model.addConstr(x[i] + x[j] <= 1)

    model.optimize()
    model.write("debug.lp")
    if model.status == GRB.OPTIMAL:
        selected_indices = [i for i in range(len(lessons)) if x[i].X > 0.5]
        return [lessons[i] for i in selected_indices]
    else:
        raise RuntimeError(f"Gurobi failed. Status: {model.status}")