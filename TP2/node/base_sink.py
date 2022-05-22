import logging
import threading
import zmq
from base_node import BaseNode


class BaseSink(BaseNode):
    def __init__(self, *args):
        super().__init__(*args)

        reply_port = int(self.network_config[f"{self.node_type}_reply_port"])
        self.reply_socket = self.context.socket(zmq.REP)
        self.reply_socket.bind(f"tcp://*:{reply_port}")

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
                self.reply_socket.send_string(self.reply(msg))
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
        self.reply_process.join()
        self.pull_process.join()
        super().shutdown()

    def work(self, msg):
        raise NotImplementedError

    def reply(self, msg):
        raise NotImplementedError
