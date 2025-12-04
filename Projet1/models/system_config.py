class SystemConfiguration:
    def __init__(self, cpu_max=100, ram_max=16, threads_max=32,
                 time_max=None, min_critical=0, max_low=None):
        self.cpu_max = cpu_max
        self.ram_max = ram_max
        self.threads_max = threads_max
        self.time_max = time_max
        self.min_critical = min_critical
        self.max_low = max_low

    def to_dict(self):
        return {
            'cpu_max': self.cpu_max,
            'ram_max': self.ram_max,
            'threads_max': self.threads_max,
            'time_max': self.time_max,
            'min_critical': self.min_critical,
            'max_low': self.max_low
        }