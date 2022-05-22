import zmq
import logging


class Server:
    def __init__(self, port, posts_worker_host):
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.PULL)
        self.socket.bind(f"tcp://*:{port}")

        self.posts_worker = self.context.socket(zmq.PUSH)
        self.posts_worker.connect(
            f"tcp://{posts_worker_host[0]}:{posts_worker_host[1]}"
        )

        self.running = True

    def run(self):
        while self.running:
            try:
                msg = self.socket.recv_json()
                if msg["type"] == "post":
                    self.posts_worker.send_json(msg)
            except zmq.ZMQError as e:
                # If we are on a "Socket operation on non-socket" error,
                # and we are not running anymore, that means we called shutdown()
                # and we can safely break our while loop
                if e.errno == zmq.ENOTSOCK and not self.running:
                    break
                raise e

    def shutdown(self):
        self.socket.setsockopt(zmq.LINGER, 0)
        self.socket.close()
        self.context.term()
        self.running = False
