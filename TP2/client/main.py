import json
import os
from configparser import ConfigParser
import threading
import signal
import time
import csv
import zmq


def main():
    config = ConfigParser()
    config.read("./config.ini")

    data_dir = "./data"

    test_lines = int(os.environ.get("TEST_LINES", 0))
    server_alias = config["DEFAULT"]["server_alias"]
    server_port = int(config["DEFAULT"]["server_port"])

    is_shutdown = threading.Event()
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.connect(f"tcp://{server_alias}:{server_port}")

    signal.signal(signal.SIGTERM, lambda _n, _f: is_shutdown.set())

    def send_file(file_path):
        with open(file_path, newline="") as f:
            reader = csv.reader(
                f, delimiter=",", quotechar='"', quoting=csv.QUOTE_MINIMAL
            )
            for (i, row) in enumerate(reader):
                if is_shutdown.is_set():
                    break
                if test_lines and (i > test_lines):
                    break
                socket.send_string(json.dumps(row))
                socket.recv()

    threads = []
    for file_path in os.listdir(data_dir)[1:2]:
        path = os.path.join(data_dir, file_path)
        if not path.endswith(".csv"):
            continue
        thread = threading.Thread(target=send_file, args=(path,))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    socket.setsockopt(zmq.LINGER, 0)
    socket.close()
    context.term()


if __name__ == "__main__":
    main()
