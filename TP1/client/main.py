from configparser import ConfigParser
import datetime
import socket
import threading
import psutil
import sys
import multiprocessing
import signal


def get_stats():
    return {
        # https://psutil.readthedocs.io/en/latest/
        "cpu_percent": psutil.cpu_percent(interval=1),
        "cpu_freq_current": round(psutil.cpu_freq().current, 4),
        "load_avg_lastminute": psutil.getloadavg()[0],
        "memory_usage_percent": psutil.virtual_memory().percent,
        "disk_usage_percent": psutil.disk_usage("/").percent,
    }


def main():
    """Simple client that get's some system metrics and logs them in our central server.

    Ideal for having multiple replicated clients and checking if any of them are
    behaving out of the ordinary.

    It has a constant thread sending stats to the server every few seconds, while the
    main thread waits for user input, so that a user can send manual queries to the
    central server (setting up alerts, aggregate the metrics, etc)."""

    config = ConfigParser()
    config.read("./config.ini")
    server_alias = config["DEFAULT"]["server_alias"]
    server_port = int(config["DEFAULT"]["server_port"])
    freq = int(config["DEFAULT"]["client_stats_frequency"]) or 10
    is_user_attached = multiprocessing.Event()
    is_shutting_down = multiprocessing.Event()

    def send_query(query, log):
        if not query:
            return
        conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        conn.connect((server_alias, server_port))

        conn.sendall(f"{query}\n".encode("utf-8"))
        response = conn.recv(1024).rstrip().decode("utf-8")
        if log:
            print(f"SEND -> {query}")
        if log:
            print(f"RECV -> {response}")
        conn.shutdown(socket.SHUT_RDWR)
        conn.close()

    def send_stats():
        # Tell the world about our stats!
        # Every freq seconds!
        while not is_shutting_down.is_set():
            stats = get_stats()
            log = not is_user_attached.is_set()
            for (metric_id, metric_value) in stats.items():
                query = f"LOG {metric_id} {metric_value}"
                send_query(query, log)
            is_shutting_down.wait(freq)

    send_stats_thread = threading.Thread(target=send_stats, args=())

    def shutdown():
        print("Shutting Down")
        is_shutting_down.set()
        send_stats_thread.join()

        # The main thread might be blocked on input()
        # So we need to interrupt it with a sys.exit()
        # Not the cleanest shutdown in the world... (but this is a dummy client)
        sys.exit(0)

    signal.signal(signal.SIGTERM, lambda _n, _f: shutdown())
    send_stats_thread.start()

    input()
    print(f"NOW -> {datetime.datetime.now().isoformat()}")
    is_user_attached.set()
    while not is_shutting_down.is_set():
        query = input("QUERY: ")
        send_query(query, True)


if __name__ == "__main__":
    main()
