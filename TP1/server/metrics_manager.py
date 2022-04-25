from statistics import mean
from datetime import datetime
from enum import Enum
import os


class AggregateOp(Enum):
    AVG = "AVG"
    MAX = "MAX"
    MIN = "MIN"
    COUNT = "COUNT"


operations = {
    AggregateOp.MIN: min,
    AggregateOp.AVG: mean,
    AggregateOp.MAX: max,
    AggregateOp.COUNT: len,
}


class MetricsManager:
    """A metrics manager where we store each metric in a separate logfile, handled by
    the file manager"""

    def __init__(self, file_manager):
        self.file_manager = file_manager

    def filename(self, metric_id):
        return os.path.join("/logs", f"{metric_id}.log")

    def to_line(self, metric_id, value, timestamp):
        """Receives a metric id, a value and the metric datetime object
        and returns a string where the time can be compared as a string (iso format)"""
        time_iso = timestamp.isoformat()
        return f"{time_iso} {metric_id} {value}\n"

    def from_line(self, line):
        """The inverse of to_line:
        goes from the string representation of a metric, to one with the correct python
        types"""
        time_iso, metric_id, value = line.split()
        timestamp = datetime.fromisoformat(time_iso)
        return (metric_id, float(value), timestamp)

    def exists(self, metric_id):
        """Checks if a metric exists in our log files"""
        filename = self.filename(metric_id)
        return self.file_manager.exists(filename)

    def insert(self, metric_id, value, timestamp):
        """Inserts a metric into it's log file, and creates it if it doesn't exist"""
        filename = self.filename(metric_id)
        line = self.to_line(metric_id, value, timestamp)
        self.file_manager.append_line(filename, line)

    def get(self, metric_id, from_date, to_date):
        """Returns every metric triplet (id, value, timestamp) of a given id,
        between two dates (inclusive)"""
        filename = self.filename(metric_id)
        from_date_iso = from_date.isoformat() if from_date else None
        to_date_iso = to_date.isoformat() if to_date else None
        lines = self.file_manager.get_lines(filename, from_date_iso, to_date_iso)
        return map(self.from_line, lines)

    def aggregate(
        self, metric_id, aggregate_op, aggregate_secs, from_date=None, to_date=None
    ):
        """Aggregates a set of metric_values in between two dates,
        grouping them first in windows of aggregate_secs seconds,
        with a given aggregation operator"""
        if not self.exists(metric_id):
            return None
        metrics = self.get(metric_id, from_date, to_date)
        grouped_values = self.group_values_by_secs(metrics, aggregate_secs)
        aggregate_op = operations[aggregate_op]
        return list(map(aggregate_op, grouped_values))

    def group_values_by_secs(self, metrics, aggregate_secs):
        """Receives a list of metrics and groups them in buckets of aggregate_secs
        seconds.

        Returns a list of lists"""
        groups = []
        group = []
        current_time = None
        for _id, metric_value, timestamp in metrics:
            if current_time is None:
                current_time = timestamp

            # Even though some metrics may be in the same second,
            #   if our window is 0 we explicitly want to proccess all of them individually
            time_ts = timestamp.timestamp()
            current_time_ts = current_time.timestamp()
            group.append(metric_value)
            if ((time_ts - current_time_ts) <= aggregate_secs) and aggregate_secs != 0:
                continue
            groups.append(group)
            group = []
            current_time = None
        return groups
