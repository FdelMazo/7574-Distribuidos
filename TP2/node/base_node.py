import logging
import zmq


class BaseNode:
    def __init__(self, node_type, network_config):
        self.node_type = node_type
        self.network_config = network_config
        _, port = self.get_host(node_type)

        self.context = zmq.Context()
        self.recver = self.context.socket(zmq.PULL)
        self.recver.bind(f"tcp://*:{port}")

        self.running = True

    def pull_loop(self):
        while self.running:
            try:
                msg = self.recver.recv_json()
                logging.debug(msg)
                self.work(msg)
            except zmq.ZMQError as e:
                # If we are on a "Socket operation on non-socket" error,
                # and we are not running anymore, that means we called shutdown()
                # and we can safely break our while loop
                if e.errno == zmq.ENOTSOCK and not self.running:
                    break
                raise e

    def start(self):
        self.pull_loop()

    def shutdown(self):
        self.recver.setsockopt(zmq.LINGER, 0)
        self.recver.close()
        self.context.term()
        self.running = False

    def get_host(self, node_type):
        hostname = self.network_config[f"{node_type}_hostname"]
        port = int(self.network_config[f"{node_type}_port"])
        return (hostname, port)

    def work(self, msg):
        raise NotImplementedError
