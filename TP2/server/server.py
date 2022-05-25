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

        # Our metrics are a simple dict that we can send as a json through the network
        self.metrics = {}
        self.is_shutdown = threading.Event()

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
                self.reply_socket.send_json(self.metrics)
            except zmq.ZMQError as e:
                # If we are on a "Socket operation on non-socket" or on a
                # "Context was terminated" error and we are not running anymore, that
                # means we called shutdown() and we can safely break our while loop
                if (
                    e.errno == zmq.ENOTSOCK or e.errno == zmq.ETERM
                ) and not self.running:
                    break
                raise e

    def pull_loop(self):
        """
        This loop constantly pulls metrics from the PULL socket and updates the
        self.metrics dictionary, serving as the final sink of the DAG. 

        Metrics consists of a name, a value, and an optional 'metric_encoded' boolean
        that indicates that the value is a base64 encoded string.

        We currently don't have any special restriction on the request, it can be any
        string whatsoever.
        """

        while not self.is_shutdown.is_set():
            try:
                msg = self.pull_socket.recv_json()

                # If the metric is encoded we don't want to log it, as it will be a big
                # blob of base64 data that will clutter the whole log
                if msg.get("metric_encoded"):
                    logging.debug({k: v for k, v in msg.items() if k != "metric_value"})
                else:
                    logging.debug(msg)

                self.metrics[msg["metric_name"]] = {
                    # We store the whole message except for the 'metric_name' which now
                    # serves as the dict key
                    k: v for k, v in msg.items() if k != "metric_name"
                }
            except zmq.ZMQError as e:
                # If we are on a "Socket operation on non-socket" or on a
                # "Context was terminated" error and we are not running anymore, that
                # means we called shutdown() and we can safely break our while loop
                if (
                    e.errno == zmq.ENOTSOCK or e.errno == zmq.ETERM
                ) and not self.running:
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
