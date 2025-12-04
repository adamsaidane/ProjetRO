from Projet1.models.process import Process


def create_example_processes():
    processes = [
        Process("WebServer", 100, 15, 2.0, 4, 1, 360),
        Process("Database", 150, 25, 4.0, 8, 1, 720),
        Process("Cache", 80, 10, 1.5, 2, 2, 180),
        Process("Analytics", 70, 20, 3.0, 6, 3, 540),
        Process("Backup", 40, 15, 2.5, 4, 3, 900),
        Process("Monitoring", 60, 8, 1.0, 2, 2, 120),
        Process("Logging", 30, 5, 0.5, 1, 4, 60),
        Process("TestEnv", 20, 12, 2.0, 3, 4, 360),
    ]

    # Ajouter des dépendances
    processes[2].add_dependency("Database")  # Cache dépend de Database
    processes[3].add_dependency("Database")  # Analytics dépend de Database

    # Ajouter des incompatibilités
    processes[7].add_incompatibility("WebServer")  # TestEnv incompatible avec WebServer
    processes[0].add_incompatibility("TestEnv")

    return processes