import gurobipy as gp
from gurobipy import GRB
import numpy as np
from typing import List, Tuple, Dict, Optional
import time
from dataclasses import dataclass


@dataclass
class Solution:
    """Container for solver results"""
    routes: List[List[int]]
    total_distance: float
    total_time: float  # Total time including travel + service
    travel_time: float  # Just travel time
    service_time: float  # Just service time
    status: str
    solve_time: float
    node_count: int = 0
    gap: float = 0.0
    vehicle_counts: List[int] = None


class PersonnelRoutingSolver:
    """Optimized solver for sales representative routing with multiple vehicles"""

    def __init__(self, time_limit: int = 30, mip_gap: float = 0.01):
        self.time_limit = time_limit
        self.mip_gap = mip_gap
        self.model = None
        self.solution = None

    def create_distance_matrix(self, locations: List[Tuple[float, float]]) -> np.ndarray:
        """Create Euclidean distance matrix"""
        n = len(locations)
        dist_matrix = np.zeros((n, n))

        for i in range(n):
            for j in range(n):
                if i != j:
                    xi, yi = locations[i]
                    xj, yj = locations[j]
                    dist_matrix[i][j] = np.sqrt((xi - xj) ** 2 + (yi - yj) ** 2)

        return dist_matrix

    def solve_vrp(self,
                  distances: np.ndarray,
                  n_vehicles: int = 1,
                  vehicle_capacities: List[int] = None,
                  demands: List[int] = None,
                  service_times: Optional[List[float]] = None) -> Solution:
        """
        Solve Vehicle Routing Problem (VRP) with multiple vehicles

        Args:
            distances: n x n distance matrix (in km)
            n_vehicles: number of vehicles/sales representatives
            vehicle_capacities: maximum clients per vehicle
            demands: demand at each client location (typically 1 per client)
            service_times: Service time at each location (in minutes)

        Returns:
            Solution object containing routes and metrics
        """
        start_time = time.time()
        n = len(distances)  # n includes depot (index 0)

        if service_times is None:
            service_times = [0] * n  # Depot has 0 service time

        if demands is None:
            demands = [0] * n  # Depot has 0 demand

        if vehicle_capacities is None:
            # Default capacity: unlimited
            vehicle_capacities = [1000] * n_vehicles

        try:
            # Create model
            self.model = gp.Model("Sales_Representatives_Routing")
            self.model.setParam('TimeLimit', self.time_limit)
            self.model.setParam('MIPGap', self.mip_gap)
            self.model.setParam('OutputFlag', 0)

            # Variables: x[i,j,k] = 1 if vehicle k travels from i to j
            x = {}
            for i in range(n):
                for j in range(n):
                    if i != j:
                        for k in range(n_vehicles):
                            x[i, j, k] = self.model.addVar(
                                vtype=GRB.BINARY,
                                name=f"x_{i}_{j}_{k}"
                            )

            # Variables: u[i,k] = position of node i in route k (for MTZ)
            u = {}
            for i in range(n):
                for k in range(n_vehicles):
                    u[i, k] = self.model.addVar(
                        vtype=GRB.CONTINUOUS,
                        lb=0,
                        ub=n - 1,
                        name=f"u_{i}_{k}"
                    )

            # Objective: minimize total travel time
            # Assume average speed: 50 km/h (0.833 km/min)
            speed_km_per_min = 0.833  # 50 km/h = 0.833 km/min

            # Travel time in minutes
            travel_times = distances / speed_km_per_min

            obj = gp.quicksum(
                travel_times[i][j] * x[i, j, k]
                for i in range(n) for j in range(n) if i != j
                for k in range(n_vehicles)
            )
            self.model.setObjective(obj, GRB.MINIMIZE)

            # Constraints

            # 1. Each client visited exactly once (excluding depot)
            for j in range(1, n):
                self.model.addConstr(
                    gp.quicksum(x[i, j, k]
                                for i in range(n) if i != j
                                for k in range(n_vehicles)) == 1,
                    name=f"visit_{j}"
                )

            # 2. Each vehicle starts and ends at depot
            for k in range(n_vehicles):
                # Vehicle leaves depot
                self.model.addConstr(
                    gp.quicksum(x[0, j, k] for j in range(1, n)) == 1,
                    name=f"leave_depot_{k}"
                )
                # Vehicle returns to depot
                self.model.addConstr(
                    gp.quicksum(x[i, 0, k] for i in range(1, n)) == 1,
                    name=f"return_depot_{k}"
                )

            # 3. Flow conservation for each vehicle
            for k in range(n_vehicles):
                for h in range(n):  # intermediate nodes
                    if h != 0:  # not depot
                        self.model.addConstr(
                            gp.quicksum(x[i, h, k] for i in range(n) if i != h) -
                            gp.quicksum(x[h, j, k] for j in range(n) if j != h) == 0,
                            name=f"flow_{h}_{k}"
                        )

            # 4. MTZ subtour elimination constraints
            for k in range(n_vehicles):
                for i in range(1, n):
                    for j in range(1, n):
                        if i != j:
                            self.model.addConstr(
                                u[i, k] - u[j, k] + (n - 1) * x[i, j, k] <= n - 2,
                                name=f"mtz_{i}_{j}_{k}"
                            )
                # Bound u variables
                for i in range(1, n):
                    self.model.addConstr(u[i, k] >= 1, name=f"u_min_{i}_{k}")
                    self.model.addConstr(u[i, k] <= n - 1, name=f"u_max_{i}_{k}")

            # 5. Capacity constraints (maximum clients per vehicle)
            if any(d > 0 for d in demands):
                for k in range(n_vehicles):
                    capacity = vehicle_capacities[k]
                    # Sum of demands on route k <= capacity
                    self.model.addConstr(
                        gp.quicksum(
                            demands[j] * gp.quicksum(x[i, j, k] for i in range(n) if i != j)
                            for j in range(1, n)
                        ) <= capacity,
                        name=f"capacity_{k}"
                    )

            # Optimize
            self.model.optimize()

            # Extract solution
            if self.model.status == GRB.OPTIMAL or self.model.status == GRB.TIME_LIMIT:
                routes = self._extract_routes(x, n, n_vehicles)

                # Calculate total travel time
                total_travel_time = self.model.objVal  # Travel time in minutes

                # Calculate total service time for visited clients
                total_service_time = 0
                for route in routes:
                    for node in route:
                        if node != 0:  # Not depot
                            total_service_time += service_times[node]

                total_time_minutes = total_travel_time + total_service_time

                # Calculate total distance
                total_distance = 0
                for route in routes:
                    for i in range(len(route) - 1):
                        from_node = route[i]
                        to_node = route[i + 1]
                        total_distance += distances[from_node][to_node]

                self.solution = Solution(
                    routes=routes,
                    total_distance=total_distance,
                    total_time=total_time_minutes,
                    travel_time=total_travel_time,
                    service_time=total_service_time,
                    status=self.model.status,
                    solve_time=time.time() - start_time,
                    node_count=self.model.NodeCount,
                    gap=self.model.MIPGap,
                    vehicle_counts=[len(route) - 2 for route in routes]  # exclude depot at start and end
                )

                return self.solution
            else:
                return Solution([], 0, 0, 0, 0, "Infeasible", time.time() - start_time)

        except gp.GurobiError as e:
            print(f"Gurobi error: {e}")
            return Solution([], 0, 0, 0, 0, f"Error: {e}", time.time() - start_time)
        except Exception as e:
            print(f"Unexpected error: {e}")
            return Solution([], 0, 0, 0, 0, f"Error: {e}", time.time() - start_time)

    def _extract_routes(self, x: Dict, n: int, n_vehicles: int) -> List[List[int]]:
        """Extract routes for all vehicles from solution variables"""
        routes = []

        for k in range(n_vehicles):
            # Start each route at depot
            route = [0]
            current = 0

            # Follow the path for vehicle k
            while True:
                found = False
                for j in range(n):
                    if j != current and (current, j, k) in x:
                        if x[current, j, k].X > 0.5:  # Variable is 1
                            route.append(j)
                            current = j
                            found = True
                            break

                if not found or current == 0:
                    break

            # Add depot at end if not already there
            if route[-1] != 0:
                route.append(0)

            # Only add non-empty routes (not just depot->depot)
            if len(route) > 2:
                routes.append(route)

        return routes

    def save_solution(self, filename: str):
        """Save solution to file"""
        if self.solution and self.model:
            with open(filename, 'w') as f:
                f.write("=== Sales Representatives Routing Solution ===\n")
                f.write(f"Status: {self.solution.status}\n")
                f.write(f"Total Distance: {self.solution.total_distance:.2f} km\n")
                f.write(f"Total Time: {self.solution.total_time:.1f} min\n")
                f.write(f"  - Travel Time: {self.solution.travel_time:.1f} min\n")
                f.write(f"  - Service Time: {self.solution.service_time:.1f} min\n")
                f.write(f"Solve Time: {self.solution.solve_time:.2f}s\n")
                f.write(f"MIP Gap: {self.solution.gap:.4f}\n")
                f.write(f"Nodes explored: {self.solution.node_count}\n")

                for i, route in enumerate(self.solution.routes):
                    f.write(f"\nSales Representative {i + 1} Route:\n")
                    f.write(" -> ".join(["Depot" if node == 0 else f"Client {node}" for node in route]))
                    if self.solution.vehicle_counts:
                        f.write(f" ({self.solution.vehicle_counts[i]} clients)")
                    f.write("\n")