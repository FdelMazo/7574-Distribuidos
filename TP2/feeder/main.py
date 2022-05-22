import os
from configparser import ConfigParser
import threading
import signal
import csv
import zmq

def main():
    config = ConfigParser()
    config.read("./config.ini")

    data_dir = "./data"

    test_lines = int(os.environ.get("TEST_LINES", 0))
    server_host = (config["NETWORK"]["server_hostname"], int(config["NETWORK"]["server_port"]))

    is_shutdown = threading.Event()
    context = zmq.Context()
    socket = context.socket(zmq.PUSH)
    socket.connect(f"tcp://{server_host[0]}:{server_host[1]}")

    signal.signal(signal.SIGTERM, lambda _n, _f: is_shutdown.set())

    def send_file(file_path):
        with open(file_path, newline="") as f:
            reader = csv.DictReader(
                f, delimiter=",", quotechar='"', quoting=csv.QUOTE_MINIMAL
            )
            for (i, row) in enumerate(reader):
                if is_shutdown.is_set():
                    break
                if test_lines and (i >= test_lines):
                    break
                socket.send_json(row)

    threads = []
    for file_path in os.listdir(data_dir):
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
