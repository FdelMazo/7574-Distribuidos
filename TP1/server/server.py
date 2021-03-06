from datetime import datetime
import multiprocessing
import socket
import logging
from http import HTTPStatus
from enum import Enum
import os

from metrics_manager import AggregateOp


class Command(Enum):
    LOG = "LOG"
    AGGREGATE = "QUERY"
    NEW_ALERT = "NEW-ALERT"


descriptions = {
    Command.LOG: "LOG <id:str> <value:float>",
    Command.AGGREGATE: f"QUERY <id:str> <op:{'|'.join([op.value for op in AggregateOp])}> <secs:float> [from:iso_date] [to:iso_date]",
    Command.NEW_ALERT: f"NEW-ALERT <id:str> <op:{'|'.join([op.value for op in AggregateOp])}> <secs:float> <limit:float>",
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
        """Listens for new clients until the server is shut down, and handles each
        client on a different process"""

        processes = []
        with multiprocessing.Pool(None) as pool:
            while self.running:
                client_sock = self.accept()
                if not self.running:
                    break

                # On a server high load, we avoid creating a new process for the request
                # We arbitrarily assume a high load means twice our cpu count (this
                # could be a bad assumption... should it be parametrized?)
                if len(pool._cache) > os.cpu_count() * 2:
                    self.reply(
                        client_sock,
                        HTTPStatus.SERVICE_UNAVAILABLE.value,
                        f"We're busy, try again later",
                    )
                    continue

                # An async task which we .get() on a new process, so that we can keep
                # listening for new clients while we handle the current one on the bg
                response = pool.apply_async(self.handle_client, args=(client_sock,))
                process = multiprocessing.Process(
                    target=lambda r: r.get(), args=((response,))
                )

                # A little bit of garbage collection (clean up dead threads)
                if len(processes) > os.cpu_count():
                    processes = [p for p in processes if p.is_alive()]

                processes.append(process)
                process.start()

            logging.info("Shutting Down: Server Pool")
            pool.close()
            pool.join()

        logging.info("Shutting Down: Hanging Processes")
        for p in processes:
            p.join()

    def handle_client(self, client_sock):
        """Handles a client: parse the command, apply it, reply!"""
        # We ask the time as soon as we get the message!
        timestamp = datetime.now()
        try:
            # that 1024 feels hardcoded... I don't have a custom protocol for the cmds
            msg = client_sock.recv(1024).rstrip().decode("utf-8").split()
            try:
                (command, *parameters) = self.parse_msg(msg, timestamp)
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
        client_sock.sendall(f"{status_code} {msg}".encode("utf-8"))

    def apply_command(self, command, parameters):
        """Applies the command with help of our metrics and alerts managers and returns
        a tuple with the status code and the response message"""
        if command == Command.LOG:
            self.metrics_manager.insert(*parameters)
            return (HTTPStatus.CREATED.value, "Metric Inserted")
        elif command == Command.AGGREGATE:
            aggregations = self.metrics_manager.aggregate(*parameters)
            if aggregations == None:
                return (HTTPStatus.NOT_FOUND.value, "Metric Not Found")
            return (HTTPStatus.OK.value, aggregations)
        elif command == Command.NEW_ALERT:
            added = self.alert_monitor.add_alert(*parameters)
            if not added:
                return (HTTPStatus.NOT_FOUND.value, "Metric Not Found")
            return (HTTPStatus.OK.value, "Alert Registered")

    def parse_msg(self, msg, timestamp):
        """Parses the message received and returns a tuple with the command and the
        parameters.

        raises a ValueError if the message is invalid"""
        try:
            command = Command(msg[0])
        except ValueError:
            raise ValueError(f"Available commands: {[c.value for c in Command]}")

        try:
            if command == Command.LOG:
                metric_id, metric_value = msg[1], float(msg[2])
                return (command, metric_id, metric_value, timestamp)
            elif command == Command.AGGREGATE:
                metric_id, aggregate_op, aggregate_secs = (
                    msg[1],
                    AggregateOp(msg[2]),
                    float(msg[3]),
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
                    float(msg[3]),
                    float(msg[4]),
                )
                return (command, metric_id, aggregate_op, aggregate_secs, limit)
        except:
            raise ValueError(descriptions[command])
