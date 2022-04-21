class MetricsManager:
    def __init__(self, file_manager):
        self.file_manager = file_manager

    def get(self):
        pass

    def insert(self, id, value):
        filename = f"{id}.log"
        line = f"{id} {value}\n"
        self.file_manager.append_line(filename, line)

    def get_between(self, from_date, to_date):
        pass

    def aggregate(self, aggregate_op, aggregate_secs, from_date, to_date):
        pass

    def avg(self):
        pass

    def min(self):
        pass

    def max(self):
        pass

    def count(self):
        pass
