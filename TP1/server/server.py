from datetime import datetime
import multiprocessing
import socket
import logging
from http import HTTPStatus
from enum import Enum

from metrics_manager import AggregateOp


class Command(Enum):
    LOG = "LOG"
    AGGREGATE = "QUERY"
    NEW_ALERT = "NEW-ALERT"


descriptions = {
    Command.LOG: "LOG <id:str> <value:float>",
    Command.AGGREGATE: f"QUERY <id:str> <op:{'|'.join([op.value for op in AggregateOp])}> <secs:int> [from:iso_date] [to:iso_date]",
    Command.NEW_ALERT: f"NEW-ALERT <id:str> <op:{'|'.join([op.value for op in AggregateOp])}> <secs:int> <limit:float>",
}


class Server:
    """A multiprocessing TCP server which handles each client on it's own process,
    receives it's commands, applies the actions, and replies to the client"""

    def __init__(self, port, metrics_manager, alert_monitor):
        self.metrics_manager = metrics_manager
        self.alert_monitor = alert_monitor
        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_socket.bind(("", port))
        self._server_socket.listen()
        self.running = True

    def run(self):
        """Listens for new clients until the server is shut down, and handles each client on a different process"""
        with multiprocessing.Pool(None) as pool:
            while self.running:
                client_sock = self.accept()
                if not self.running:
                    break
                pool.apply(self.handle_client, args=((client_sock,)))

    def handle_client(self, client_sock):
        """Handles a client: parse the command, apply it, reply!"""
        # We ask the time as soon as we get the message!
        time = datetime.now()
        try:
            msg = client_sock.recv(1024).rstrip().decode("utf-8").split()
            try:
                (command, *parameters) = self.parse_msg(msg, time)
            except ValueError as e:
                self.reply(
                    client_sock, HTTPStatus.BAD_REQUEST.value, f"Bad Request -- {e}"
                )
                return

            (status_code, body) = self.apply_command(command, parameters)
            self.reply(client_sock, status_code, body)
        except OSError:
            logging.error(f"Error while reading socket {client_sock}")
        finally:
            client_sock.close()

    def accept(self):
        """Accepts a new client connection
        If the socket is closed (due to server shutdown), returns None"""
        try:
            c, _addr = self._server_socket.accept()
        except OSError:
            return
        return c

    def shutdown(self):
        """Shuts down the server"""
        logging.info("Shutting Down: Server Socket")
        self.running = False
        self._server_socket.shutdown(socket.SHUT_RDWR)
        self._server_socket.close()

    def reply(self, client_sock, status_code, msg):
        """Replies to the client with a status code and a message"""
        client_sock.send(f"{status_code} {msg}".encode("utf-8"))

    def apply_command(self, command, parameters):
        """Applies the command with help of our metrics and alerts managers and returns a tuple with the status code and the response message"""
        if command == Command.LOG:
            self.metrics_manager.insert(*parameters)
            return (HTTPStatus.CREATED.value, "Metric Inserted")
        elif command == Command.AGGREGATE:
            aggregations = self.metrics_manager.aggregate(*parameters)
            if not aggregations:
                return (HTTPStatus.NOT_FOUND.value, "Metric Not Found")
            return (HTTPStatus.OK.value, aggregations)
        elif command == Command.NEW_ALERT:
            added = self.alert_monitor.add_alert(*parameters)
            if not added:
                return (HTTPStatus.NOT_FOUND.value, "Metric Not Found")
            return (HTTPStatus.CREATED.value, "Alert Added")

    def parse_msg(self, msg, time):
        """Parses the message received and returns a tuple with the command and the parameters,
        raises a ValueError if the message is invalid"""
        try:
            command = Command(msg[0])
        except ValueError:
            raise ValueError(f"Available commands: {[c.value for c in Command]}")

        try:
            if command == Command.LOG:
                metric_id, metric_value = msg[1], float(msg[2])
                return (command, metric_id, metric_value, time)
            elif command == Command.AGGREGATE:
                metric_id, aggregate_op, aggregate_secs = (
                    msg[1],
                    AggregateOp(msg[2]),
                    int(msg[3]),
                )
                from_date = datetime.fromisoformat(msg[4]) if len(msg) > 4 else None
                to_date = datetime.fromisoformat(msg[5]) if len(msg) > 5 else None
                return (
                    command,
                    metric_id,
                    aggregate_op,
                    aggregate_secs,
                    from_date,
                    to_date,
                )
            elif command == Command.NEW_ALERT:
                metric_id, aggregate_op, aggregate_secs, limit = (
                    msg[1],
                    AggregateOp(msg[2]),
                    int(msg[3]),
                    float(msg[4]),
                )
                return (command, metric_id, aggregate_op, aggregate_secs, limit)
        except:
            raise ValueError(descriptions[command])
