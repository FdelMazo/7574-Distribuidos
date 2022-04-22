import time
import logging


class AlertMonitor:
    def __init__(self, metrics_manager, alerts):
        self.metrics_manager = metrics_manager
        self.alerts = alerts
        self.running = True

    def add_alert(self, metric_id, aggregate_op, aggregate_secs, limit):
        if metric_id in self.alerts:
            # Keep in mind, one can't simply append to the set inside the dict
            # We need to reassign the set to key
            # https://stackoverflow.com/a/46228938
            s = self.alerts[metric_id]
            s.add((aggregate_op, aggregate_secs, limit))
            self.alerts[metric_id] = s
        else:
            self.alerts[metric_id] = {(aggregate_op, aggregate_secs, limit)}

    def run(self):
        while self.running:
            time.sleep(5)
            for metric_id, metric_alerts in self.alerts.items():
                for (aggregate_op, aggregate_secs, limit) in metric_alerts:
                    aggregations = self.metrics_manager.aggregate(
                        metric_id, aggregate_op, aggregate_secs
                    )
                    if any([(a > limit) for a in aggregations]):
                        logging.info(
                            f"ALERT {metric_id}: {aggregate_op.value} is over {limit}"
                        )

    def shutdown(self):
        self.running = False
