import zmq
import logging
import threading


class Server:
    """
    This server is the glue that ties in the user that needs some metrics with the DAG
    that processed them.

    It has two different tasks running in constant loop:
    - It listens on one port to see if a client requested for some metrics
    - It collects the metrics that the DAG produced from another port and stores them
    """

    def __init__(self, network_config):
        self.context = zmq.Context()
        reply_port = int(network_config["server_port"])
        self.reply_socket = self.context.socket(zmq.REP)
        self.reply_socket.bind(f"tcp://*:{reply_port}")

        pull_port = int(network_config["collector_port"])
        self.pull_socket = self.context.socket(zmq.PULL)
        self.pull_socket.bind(f"tcp://*:{pull_port}")

        # Our metrics are a simple (thread-safe) dict that we can send as a json
        self.metrics = {}
        self.metrics_lock = threading.Lock()

        self.is_shutdown = threading.Event()

        # After getting an EOF, we want to have a grace window for receiving any metrics
        # still being processed. If we don't receive any kind of message after that
        # window, we can stop listening from the pull socket
        self.timeout = int(network_config["server_ms_timeout"])

    def start(self):
        # As we don't need 'real' parallelism for this two tasks, we use threads instead of processes
        self.reply_loop = threading.Thread(target=self.reply_loop)
        self.pull_loop = threading.Thread(target=self.pull_loop)
        self.reply_loop.start()
        self.pull_loop.start()

    def reply_loop(self):
        """
        This loop listens on a REP socket for a new request string and sends back 
        whatever we have on our metrics dict as a json.

        We currently don't have any special restriction on the request, it can be any
        string whatsoever
        """
        while not self.is_shutdown.is_set():
            try:
                msg = self.reply_socket.recv_string()
                logging.debug(msg)
                with self.metrics_lock:
                    self.reply_socket.send_json(self.metrics)
            except zmq.ZMQError as e:
                # If we are on a "Socket operation on non-socket" or on a
                # "Context was terminated" error and we are not running anymore, that
                # means we called shutdown() and we can safely break our while loop
                if (
                    e.errno == zmq.ENOTSOCK or e.errno == zmq.ETERM
                ) and self.is_shutdown.is_set():
                    break
                raise e

    def pull_loop(self):
        """
        This loop constantly pulls metrics from the PULL socket and updates the
        self.metrics dictionary, serving as the final sink of the DAG.

        Metrics consists of a name, a value, and an optional 'metric_encoded' boolean
        that indicates that the value is a base64 encoded string.

        This loop also has a direct connection to the source, (or whomever is
        responsible of giving the final say) to see if we should stop listening for new
        metrics and treat what we have as final values. That is specified by receiving a
        json message formatted as {'type': 'EOF'}
        """

        while not self.is_shutdown.is_set():
            try:
                msg = self.pull_socket.recv_json()
                if msg.get("type") == "EOF":
                    logging.info(f"Got EOF => Setting {self.timeout}ms timeout window")
                    self.pull_socket.setsockopt(zmq.RCVTIMEO, self.timeout)
                    continue

                # If the metric is encoded we don't want to log it, as it will be a big
                # blob of base64 data that will clutter the whole log
                if msg.get("metric_encoded"):
                    logging.debug({k: v for k, v in msg.items() if k != "metric_value"})
                else:
                    logging.debug(msg)

                with self.metrics_lock:
                    self.metrics[msg["metric_name"]] = {
                        # We store the whole message except for the 'metric_name' which now
                        # serves as the dict key
                        k: v
                        for k, v in msg.items()
                        if k != "metric_name"
                    }
            except zmq.ZMQError as e:
                # If our socket timed-out, that means we got an `EOF` message that set
                # the timeout window. We can safely assume this error means our metrics
                # are final and we can exit our loop
                if e.errno == zmq.EAGAIN:
                    logging.info(f"Timed-out after EOF => Setting metrics as final")
                    with self.metrics_lock:
                        for k in self.metrics:
                            self.metrics[k].update({"metric_final": True})
                    break

                # If we are on a "Socket operation on non-socket" or on a
                # "Context was terminated" error and we are not running anymore, that
                # means we called shutdown() and we can safely break our while loop
                if (
                    e.errno == zmq.ENOTSOCK or e.errno == zmq.ETERM
                ) and self.is_shutdown.is_set():
                    break
                raise e

    def shutdown(self):
        self.is_shutdown.set()
        self.reply_socket.setsockopt(zmq.LINGER, 0)
        self.reply_socket.close()
        self.pull_socket.setsockopt(zmq.LINGER, 0)
        self.pull_socket.close()
        self.context.term()
        self.reply_loop.join()
        self.pull_loop.join()
