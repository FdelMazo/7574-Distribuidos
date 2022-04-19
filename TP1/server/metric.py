class Metric:
    def __init__(self, id):
        self.id = id

    def get(self):
        pass

    def insert(self, value):
        pass

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
