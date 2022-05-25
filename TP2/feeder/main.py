import os
from configparser import ConfigParser
import threading
import signal
import csv
import zmq
import time
import random


def main():
    config = ConfigParser()
    config.read("./config.ini")

    test_lines = int(os.environ.get("TEST_LINES", 0))
    source_host = (
        config["NETWORK"]["source_hostname"],
        int(config["NETWORK"]["source_port"]),
    )

    is_shutdown = threading.Event()
    posts_file, comments_file = (
        config["FEEDER"]["posts_file"],
        config["FEEDER"]["comments_file"],
    )
    context = zmq.Context()
    socket = context.socket(zmq.PUSH)
    socket.connect(f"tcp://{source_host[0]}:{source_host[1]}")

    signal.signal(signal.SIGTERM, lambda _n, _f: is_shutdown.set())

    with open(posts_file, newline="") as posts, open(
        comments_file, newline=""
    ) as comments:
        posts_reader = csv.DictReader(
            posts, delimiter=",", quotechar='"', quoting=csv.QUOTE_MINIMAL
        )
        comments_reader = csv.DictReader(
            comments, delimiter=",", quotechar='"', quoting=csv.QUOTE_MINIMAL
        )

        i, j = 0, 0
        comments_row, posts_row = None, None
        while not is_shutdown.is_set():
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

            if not comments_row and not posts_row:
                break
            if test_lines and (i + j >= test_lines):
                break

    print(f"Finished sending {i+j} lines from {posts_file} and {comments_file}")

    socket.setsockopt(zmq.LINGER, 0)
    socket.close()
    context.term()


if __name__ == "__main__":
    main()
