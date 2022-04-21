import time


class _Alert:
    def __init__(self, metric, metric_limit, aggregate_op, aggregate_secs):
        self.metric = metric
        self.metric_limit = metric_limit
        self.aggregate_op = aggregate_op
        self.aggregate_secs = aggregate_secs

    def verify(self):
        pass


class AlertMonitor:
    def __init__(self, metrics_manager):
        self.metrics_manager = metrics_manager
        self.running = True

    def run(self):
        print("ALERTING")
        while self.running:
            time.sleep(3)
            print("AlertMonitor: loop")

    def verify(self):
        pass

    def signal(self):
        pass

    def loop(self):
        pass

    def shutdown(self):
        self.running = False
