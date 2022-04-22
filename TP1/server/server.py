from datetime import datetime
import multiprocessing
import socket
import logging


class Server:
    def __init__(self, port, metrics_manager):
        self.metrics_manager = metrics_manager
        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_socket.bind(("", port))
        self._server_socket.listen()
        self.running = True

    def run(self):
        with multiprocessing.Pool(None) as pool:
            while self.running:
                client_sock = self.accept()
                if not self.running:
                    break
                pool.apply(self.handle_client, args=((client_sock,)))

    def handle_client(self, client_sock):
        try:
            msg = client_sock.recv(1024).rstrip().decode("utf-8").split()
            command = msg[0]
            time = datetime.now()
            timestamp = datetime.timestamp(time)
            if command == "LOG":
                metric_id, metric_value = msg[1], msg[2]
                self.metrics_manager.insert(metric_id, metric_value, timestamp)
            elif command == "QUERY":
                metric_id, aggregate_op, aggregate_secs = msg[1], msg[2], int(msg[3])
                from_date = msg[4] if len(msg) > 4 else None
                to_date = msg[5] if len(msg) > 5 else None
                self.metrics_manager.aggregate(
                    metric_id, aggregate_op, aggregate_secs, from_date, to_date
                )
            elif command == "NEW-ALERT":
                metric_id, aggregate_op, aggregate_secs, limit = (
                    msg[1],
                    msg[2],
                    msg[3],
                    msg[4],
                )
            else:
                logging.info(
                    "Message received from connection {}. Msg: {}".format(
                        client_sock.getpeername(), msg
                    )
                )
            client_sock.send("200 Metric Inserted".encode("utf-8"))
        except OSError:
            logging.info("Error while reading socket {}".format(client_sock))
        finally:
            client_sock.close()

    def accept(self):
        try:
            c, _addr = self._server_socket.accept()
        except OSError:
            return
        return c

    def shutdown(self):
        logging.info("Shutting down (socket)")
        self.running = False
        self._server_socket.shutdown(socket.SHUT_RDWR)
        self._server_socket.close()
