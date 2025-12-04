class OptimizationResult:
    def __init__(self, status, objective_value=None, selected_processes=None,
                 total_cpu=0, total_ram=0, total_threads=0, total_time=0):
        self.status = status
        self.objective_value = objective_value
        self.selected_processes = selected_processes or []
        self.total_cpu = total_cpu
        self.total_ram = total_ram
        self.total_threads = total_threads
        self.total_time = total_time

    def to_dict(self):
        from Projet1.models.process import Process
        return {
            'status': self.status,
            'objective_value': self.objective_value,
            'selected_processes': [p.to_dict() if isinstance(p, Process) else p
                                   for p in self.selected_processes],
            'total_cpu': self.total_cpu,
            'total_ram': self.total_ram,
            'total_threads': self.total_threads,
            'total_time': self.total_time
        }