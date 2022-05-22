import zmq
import logging


class Server:
    def __init__(self, network_config):
        self.context = zmq.Context()
        port = int(network_config["server_port"])
        self.reply_socket = self.context.socket(zmq.REP)
        self.reply_socket.bind(f"tcp://*:{port}")

        posts_collector_host = (
            network_config["posts_collector_hostname"],
            int(network_config["posts_collector_reply_port"]),
        )

        self.posts_collector = self.context.socket(zmq.REQ)
        self.posts_collector.connect(
            f"tcp://{posts_collector_host[0]}:{posts_collector_host[1]}"
        )

        self.running = True

    def run(self):
        while self.running:
            try:
                msg = self.reply_socket.recv_string()
                logging.debug(msg)
                if msg == "/post_avg_score":
                    logging.debug(msg)
                    self.posts_collector.send_string(msg)
                    avg_score = self.posts_collector.recv_string()
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
        self.posts_collector.setsockopt(zmq.LINGER, 0)
        self.posts_collector.close()
        self.context.term()
        self.running = False
