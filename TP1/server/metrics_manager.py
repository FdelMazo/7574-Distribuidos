from statistics import mean

operations = {
    "AVG": mean,
    "MIN": min,
    "MAX": max,
    "COUNT": len,
}


class MetricsManager:
    def __init__(self, file_manager):
        self.file_manager = file_manager

    def filename(self, metric_id):
        return f"{metric_id}.log"

    def to_line(self, metric_id, value, timestamp):
        return f"{timestamp} {metric_id} {value}\n"

    def from_line(self, line):
        timestamp, metric_id, value = line.split()
        return (metric_id, float(value), float(timestamp))

    def insert(self, metric_id, value, timestamp):
        filename = self.filename(metric_id)
        line = self.to_line(metric_id, value, timestamp)
        self.file_manager.append_line(filename, line)

    def get(self, metric_id, from_date, to_date):
        filename = self.filename(metric_id)
        lines = self.file_manager.get_lines(filename)
        return map(self.from_line, lines)

    def aggregate(self, metric_id, aggregate_op, aggregate_secs, from_date, to_date):
        metrics = self.get(metric_id, from_date, to_date)
        grouped_values = self.group_values_by_secs(metrics, aggregate_secs)
        aggregate_op = operations[aggregate_op]
        return list(map(aggregate_op, grouped_values))

    def group_values_by_secs(self, metrics, aggregate_secs):
        groups = []
        group = []
        current_ts = None
        for _id, metric_value, timestamp in metrics:
            if current_ts is None:
                current_ts = timestamp

            # Even though some metrics may be in the same second,
            #   if our window is 0 we explicitly want to proccess all of them individually
            if (timestamp - current_ts) <= aggregate_secs and aggregate_secs != 0:
                group.append(metric_value)

            else:
                groups.append(group)
                group = []
                current_ts = None
        return groups
