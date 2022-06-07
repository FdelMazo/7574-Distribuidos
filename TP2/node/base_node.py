import logging
import zmq


class BaseNode:
    """
    Every node in our DAG consists of the same idea: pull from a socket, work the
    message received, push to the next node in the DAG.
    """

    def __init__(self, node_type, network_config):
        self.node_type = node_type
        self.network_config = network_config
        _, port = self.get_host(node_type)

        self.context = zmq.Context()
        self.recver = self.context.socket(zmq.PULL)
        self.recver.bind(f"tcp://*:{port}")

        # We store every socket in self.sockets to easily shut them down later
        self.sockets = [self.recver]

        # We keep track of how many messages this node processed
        # We log the total number of messages on shutdown, and we also log them every
        # time the number reaches a certain breakpoint (which then increases by a factor
        # of 5) as a simple health check
        self.msg_count = 0
        self.msg_breakpoint = 1

        self.running = True

    def run(self):
        while self.running:
            try:
                msg = self.recver.recv_json()
                self.msg_count += 1
                if self.msg_count == self.msg_breakpoint:
                    # logging.info(f"{self.node_type} vivito y coleando!")
                    logging.info(
                        f"{self.node_type} alive and well! Processed {self.msg_count} messages (so far)"
                    )
                    self.msg_breakpoint *= 5

                logging.debug(msg)

                # Every child class must override the work method!
                self.work(msg)
            except zmq.ZMQError as e:
                # If we are on a "Socket operation on non-socket" error,
                # and we are not running anymore, that means we called shutdown()
                # and we can safely break our while loop
                if e.errno == zmq.ENOTSOCK and not self.running:
                    break
                raise e

    def shutdown(self):
        for socket in self.sockets:
            socket.setsockopt(zmq.LINGER, 0)
            socket.close()
        self.context.term()
        logging.info(f"Shutting Down: Processed {self.msg_count} messages")
        self.running = False

    def get_host(self, node_type):
        """
        Return the hostname and port of the node of the given type, looking them in our
        configuration
        """
        hostname = self.network_config[f"{node_type}_hostname"]
        port = int(self.network_config[f"{node_type}_port"])
        return (hostname, port)

    def push_socket(self, node_type):
        """
        Connect to a new PUSH socket, add it to our self.sockets list, and return it for
        the child class to use
        """
        hostname, port = self.get_host(node_type)
        socket = self.context.socket(zmq.PUSH)
        socket.connect(f"tcp://{hostname}:{port}")
        self.sockets.append(socket)
        return socket

    def pick_keys(self, msg, keys):
        """
        Helper function to filter out keys from a big msg, reducing the payload size and
        making sure that we are sending only the stuff we need
        """
        return {k: v for k, v in msg.items() if k in keys}

    def work(self, msg):
        raise NotImplementedError
