class Process:
    def __init__(self, name, value, cpu, ram, threads, priority, duration=0):
        self.name = name
        self.value = value
        self.cpu = cpu
        self.ram = ram
        self.threads = threads
        self.priority = priority
        self.duration = duration
        self.dependencies = []
        self.incompatible_with = []

    def add_dependency(self, process_name):
        if process_name not in self.dependencies:
            self.dependencies.append(process_name)

    def add_incompatibility(self, process_name):
        if process_name not in self.incompatible_with:
            self.incompatible_with.append(process_name)

    def to_dict(self):
        return {
            'name': self.name,
            'value': self.value,
            'cpu': self.cpu,
            'ram': self.ram,
            'threads': self.threads,
            'priority': self.priority,
            'duration': self.duration,
            'dependencies': self.dependencies.copy(),
            'incompatible_with': self.incompatible_with.copy()
        }

    @classmethod
    def from_dict(cls, data):
        proc = cls(
            data['name'],
            data['value'],
            data['cpu'],
            data['ram'],
            data['threads'],
            data['priority'],
            data.get('duration', 0)
        )
        proc.dependencies = data.get('dependencies', []).copy()
        proc.incompatible_with = data.get('incompatible_with', []).copy()
        return proc