import zmq
import logging


class Server:
    def __init__(self, network_config):
        self.context = zmq.Context()
        port = int(network_config["server_port"])
        self.reply_socket = self.context.socket(zmq.REP)
        self.reply_socket.bind(f"tcp://*:{port}")

        collector_host = (
            network_config["collector_hostname"],
            int(network_config["collector_reply_port"]),
        )

        self.collector = self.context.socket(zmq.REQ)
        self.collector.connect(f"tcp://{collector_host[0]}:{collector_host[1]}")

        self.running = True

    def run(self):
        while self.running:
            try:
                msg = self.reply_socket.recv_string()
                logging.debug(msg)
                if msg == "/post_avg_score":
                    logging.debug(msg)
                    self.collector.send_string(msg)
                    avg_score = self.collector.recv_string()
                    self.reply_socket.send_string(avg_score)
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
        self.collector.setsockopt(zmq.LINGER, 0)
        self.collector.close()
        self.context.term()
        self.running = False
