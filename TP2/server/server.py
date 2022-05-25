import zmq
import logging
import threading


class Server:
    def __init__(self, network_config):
        self.metrics = {}
        self.context = zmq.Context()
        reply_port = int(network_config["server_port"])
        self.reply_socket = self.context.socket(zmq.REP)
        self.reply_socket.bind(f"tcp://*:{reply_port}")

        pull_port = int(network_config["collector_port"])
        self.pull_socket = self.context.socket(zmq.PULL)
        self.pull_socket.bind(f"tcp://*:{pull_port}")

        self.running = True

    def start(self):
        self.reply_process = threading.Thread(target=self.reply_loop)
        self.pull_process = threading.Thread(target=self.pull_loop)
        self.reply_process.start()
        self.pull_process.start()

    def reply_loop(self):
        while self.running:
            try:
                msg = self.reply_socket.recv_string()
                logging.debug(msg)
                self.reply_socket.send_json(self.metrics)
            except zmq.ZMQError as e:
                # If we are on a "Socket operation on non-socket" error,
                # and we are not running anymore, that means we called shutdown()
                # and we can safely break our while loop
                if e.errno == zmq.ENOTSOCK and not self.running:
                    break
                raise e

    def pull_loop(self):
        while self.running:
            try:
                msg = self.pull_socket.recv_json()
                if msg.get("metric_encoded"):
                    logging.debug({k: v for k, v in msg.items() if k != "metric_value"})
                else:
                    logging.debug(msg)
                self.metrics[msg["metric_name"]] = {
                    k: v for k, v in msg.items() if k != "metric_name"
                }
            except zmq.ZMQError as e:
                # If we are on a "Socket operation on non-socket" error,
                # and we are not running anymore, that means we called shutdown()
                # and we can safely break our while loop
                if e.errno == zmq.ENOTSOCK and not self.running:
                    break
                raise e

    def shutdown(self):
        self.reply_socket.setsockopt(zmq.LINGER, 0)
        self.reply_socket.close()
        self.pull_socket.setsockopt(zmq.LINGER, 0)
        self.pull_socket.close()
        self.context.term()
        self.running = False
        self.reply_process.join()
        self.pull_process.join()
