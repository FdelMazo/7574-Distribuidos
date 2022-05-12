import json
import logging
import zmq


class Server:
    def __init__(self, port):
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REP)
        self.socket.bind(f"tcp://*:{port}")
        self.running = True

    def run(self):
        while self.running:
            try:
                msg = json.loads(self.socket.recv())
                logging.info(msg)
                self.socket.send_string("OK")
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
