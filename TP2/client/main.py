from configparser import ConfigParser
import zmq
import threading
import signal
import base64
import os


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
            socket.send_string("/everything_everywhere_all_at_once")
            reply = socket.recv_json()
            if reply:
                print("\nGot some stuff from the server!")
            for metric_name, metric in reply.items():
                if metric.get("metric_encoded"):
                    img = base64.b64decode(metric["metric_value"].encode("ascii"))
                    filepath = f"./memes/{metric_name}.jpg"

                    if not os.path.exists(filepath) or os.path.getsize(filepath) != len(img):
                        with open(filepath, "wb") as f:
                            f.write(img)
                            print(f"* saving {filepath}")
                else:
                    print(f"* {metric_name}: {metric['metric_value']}")
            is_shutting_down.wait(10)

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
