import logging
import zmq


class BaseNode:
    def __init__(self, port, network_config):
        self.context = zmq.Context()
        self.network_config = network_config

        self.recver = self.context.socket(zmq.PULL)
        self.recver.bind(f"tcp://*:{port}")

        self.running = True

    def run(self):
        while self.running:
            try:
                msg = self.recver.recv_json()
                self.work(msg)
            except zmq.ZMQError as e:
                # If we are on a "Socket operation on non-socket" error,
                # and we are not running anymore, that means we called shutdown()
                # and we can safely break our while loop
                if e.errno == zmq.ENOTSOCK and not self.running:
                    break
                raise e

    def shutdown(self):
        self.recver.setsockopt(zmq.LINGER, 0)
        self.recver.close()
        self.context.term()
        self.running = False

    def work(self, msg):
        raise NotImplementedError
