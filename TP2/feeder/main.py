import os
from configparser import ConfigParser
import threading
import signal
import csv
import zmq
import random
import time

def main():
    """
    This data feeder simulates the idea of having a constant stream of data entering
    our system, by reading csv files and pushing them row by row (as dicts) to the DAG
    source.

    It reads from two csvs (posts and comments) and sends them, indiscriminately (the
    DAG will then sort them out according to their type)
    """

    config = ConfigParser()
    config.read("./config.ini")

    # We can set up an env var 'TEST_LINES' to limit the number of rows sent
    test_lines = int(os.environ.get("TEST_LINES", 0))
    source_host = (
        config["NETWORK"]["source_hostname"],
        int(config["NETWORK"]["source_port"]),
    )
    posts_file, comments_file = (
        config["FEEDER"]["posts_file"],
        config["FEEDER"]["comments_file"],
    )

    # Have a dedicated event to track if we are shutting down (on SIGTERMs) and need to
    # stop our loop
    is_shutdown = threading.Event()
    signal.signal(signal.SIGTERM, lambda _n, _f: is_shutdown.set())

    context = zmq.Context()
    socket = context.socket(zmq.PUSH)
    socket.connect(f"tcp://{source_host[0]}:{source_host[1]}")

    with open(posts_file) as posts, open(comments_file) as comments:
        posts_reader = csv.DictReader(
            posts, delimiter=",", quotechar='"', quoting=csv.QUOTE_MINIMAL
        )
        comments_reader = csv.DictReader(
            comments, delimiter=",", quotechar='"', quoting=csv.QUOTE_MINIMAL
        )

        comments_row, posts_row = None, None
        i, j = 0, 0
        while not is_shutdown.is_set():
            # We randomly send data to the system
            # We prefer sending posts over comments as those are more valuable to the
            # system, but in reality we should have a bigger influx of comments than
            # posts
            coin_toss = random.random()
            if coin_toss <= 0.75:
                posts_row = next(posts_reader, None)
                if posts_row:
                    socket.send_json(posts_row)
                    i += 1
            else:
                comments_row = next(comments_reader, None)
                if comments_row:
                    socket.send_json(comments_row)
                    j += 1

            # Breaking conditions:
            # - SIGTERM
            if is_shutdown.is_set():
                break
            # - Finished sending our n test lines
            if test_lines and (i + j >= test_lines):
                break
            # - End of file for both csvs
            if not comments_row and not posts_row:
                break
        # Wait a bit before shutting down
        time.sleep(5)

    print(f"Finished sending {i+j} lines from {posts_file} and {comments_file}")
    print(f"Sending EOF")
    socket.send_json({'type': 'EOF'})

    socket.setsockopt(zmq.LINGER, 0)
    socket.close()
    context.term()


if __name__ == "__main__":
    main()
