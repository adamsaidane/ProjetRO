import json
import csv
import random
import numpy as np
from typing import List, Tuple, Dict, Any


class DataManager:
    """Manages problem data generation and persistence for sales representatives routing"""

    @staticmethod
    def generate_sample_data(n_clients: int = 15,
                             grid_size: int = 100) -> Dict[str, Any]:
        """Generate random but realistic sales routing data"""
        data = {
            "depot": {"id": 0, "x": grid_size / 2, "y": grid_size / 2, "name": "Office"},
            "clients": [],
            "distance_matrix": None,
            "service_times": [0],  # Depot has 0 service time
            "priorities": [2]  # Depot priority (medium)
        }

        # Generate client locations
        clients = []
        for i in range(1, n_clients + 1):
            client = {
                "id": i,
                "x": random.uniform(5, grid_size - 5),  # Avoid edges
                "y": random.uniform(5, grid_size - 5),
                "name": f"Client_{i}",
                "demand": 1,  # Each client requires 1 visit
                "service_time": random.randint(20, 60),  # 20-60 minutes service time
                "priority": random.choices([1, 2, 3], weights=[0.2, 0.5, 0.3])[0]  # 1=high, 2=medium, 3=low
            }
            clients.append(client)
            data["service_times"].append(client["service_time"])
            data["priorities"].append(client["priority"])

        data["clients"] = clients

        # Create locations list for distance matrix
        locations = [(data["depot"]["x"], data["depot"]["y"])]
        locations.extend([(c["x"], c["y"]) for c in clients])

        # Calculate distance matrix (in km)
        from solver import PersonnelRoutingSolver
        solver = PersonnelRoutingSolver()
        data["distance_matrix"] = solver.create_distance_matrix(locations)

        return data

    @staticmethod
    def save_to_json(data: Dict[str, Any], filename: str):
        """Save data to JSON file"""
        # Convert numpy arrays to lists
        serializable_data = data.copy()
        if "distance_matrix" in serializable_data:
            serializable_data["distance_matrix"] = serializable_data["distance_matrix"].tolist()

        with open(filename, 'w') as f:
            json.dump(serializable_data, f, indent=2)

    @staticmethod
    def load_from_json(filename: str) -> Dict[str, Any]:
        """Load data from JSON file"""
        with open(filename, 'r') as f:
            data = json.load(f)

        # Convert lists back to numpy arrays if needed
        if "distance_matrix" in data:
            data["distance_matrix"] = np.array(data["distance_matrix"])

        return data