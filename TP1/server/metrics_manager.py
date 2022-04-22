from statistics import mean
from datetime import datetime, time

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

    def to_line(self, metric_id, value, time):
        time_iso = time.isoformat()
        return f"{time_iso} {metric_id} {value}\n"

    def from_line(self, line):
        time_iso, metric_id, value = line.split()
        time = datetime.fromisoformat(time_iso)
        return (metric_id, float(value), time)

    def insert(self, metric_id, value, time):
        filename = self.filename(metric_id)
        line = self.to_line(metric_id, value, time)
        self.file_manager.append_line(filename, line)

    def get(self, metric_id, from_date, to_date):
        filename = self.filename(metric_id)
        from_date_iso = from_date.isoformat() if from_date else None
        to_date_iso = to_date.isoformat() if to_date else None
        lines = self.file_manager.get_lines(filename, from_date_iso, to_date_iso)
        return map(self.from_line, lines)

    def aggregate(
        self, metric_id, aggregate_op, aggregate_secs, from_date=None, to_date=None
    ):
        metrics = self.get(metric_id, from_date, to_date)
        grouped_values = self.group_values_by_secs(metrics, aggregate_secs)
        aggregate_op = operations[aggregate_op]
        return list(map(aggregate_op, grouped_values))

    def group_values_by_secs(self, metrics, aggregate_secs):
        groups = []
        group = []
        current_time = None
        for _id, metric_value, time in metrics:
            if current_time is None:
                current_time = time

            # Even though some metrics may be in the same second,
            #   if our window is 0 we explicitly want to proccess all of them individually
            time_ts = time.timestamp()
            current_time_ts = current_time.timestamp()
            if ((time_ts - current_time_ts) <= aggregate_secs) and aggregate_secs != 0:
                group.append(metric_value)
            else:
                groups.append(group)
                group = []
                current_time = None

        if (groups == []) and (group != []):
            groups.append(group)
        return groups
