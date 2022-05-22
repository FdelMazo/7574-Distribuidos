from configparser import ConfigParser
import zmq
import threading
import signal


def main():
    config = ConfigParser()
    config.read("./config.ini")

    server_host = (
        config["NETWORK"]["server_hostname"],
        int(config["NETWORK"]["server_port"]),
    )

    is_shutting_down = threading.Event()

    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.connect(f"tcp://{server_host[0]}:{server_host[1]}")

    def query_stats():
        while not is_shutting_down.is_set():
            socket.send_string("/post_avg_score")
            print(f"Post average score: {socket.recv_string()}")
            is_shutting_down.wait(5)

    query_stats_thread = threading.Thread(target=query_stats, args=())
    query_stats_thread.start()

    def shutdown():
        is_shutting_down.set()

    signal.signal(signal.SIGTERM, lambda _n, _f: shutdown())
    query_stats_thread.join()
    socket.setsockopt(zmq.LINGER, 0)
    socket.close()
    context.term()


if __name__ == "__main__":
    main()
