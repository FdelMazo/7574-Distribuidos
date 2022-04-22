import time
import logging


class AlertMonitor:
    """Our alert monitor will be responsible for monitoring the metrics.
    It runs a loop on it's own process that will check the metrics every N seconds.
    If a metric goes over the limit, we log an alert."""

    def __init__(self, metrics_manager, alerts):
        """Keep in mind, the alerts dict must be thread safe: it will be shared between processes!
        the alert loop, and whatever process calls our add_alert method.
        (That's why instead of creating it we receive it!)"""
        self.metrics_manager = metrics_manager
        self.alerts = alerts
        self.running = True

    def add_alert(self, metric_id, aggregate_op, aggregate_secs, limit):
        """Add an alert to our monitor
        Returns False if the metric to alert on doesn't exist.
        An alert on a metric id is a triplet consisting of:
        - the aggregation operator
        - the number of seconds to aggregate over
        - the limit to check against
        Doesn't check if the specific alert (the triplet) already exists,
          it simply ignores the request"""
        if not self.metrics_manager.exists(metric_id):
            return False
        if metric_id in self.alerts:
            # Keep in mind, one can't simply append to the set inside the dict
            # We need to reassign the set to key
            # https://stackoverflow.com/a/46228938
            s = self.alerts[metric_id]
            s.add((aggregate_op, aggregate_secs, limit))
            self.alerts[metric_id] = s
        else:
            # By using a set we avoid duplicates (and an already added alert will be ignored)
            self.alerts[metric_id] = {(aggregate_op, aggregate_secs, limit)}
        return True

    def run(self):
        """Run our alert monitor loop
        We wait for N seconds,
          then aggregate all of the metrics in our dictionary
          and if any of our aggregations goes above the limit,
          we signal our alert.
        This loop will stop only if we call shutdown()"""
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
        """Stop our alert monitor loop"""
        logging.info("Shutting Down: Alert Monitor")
        self.running = False
