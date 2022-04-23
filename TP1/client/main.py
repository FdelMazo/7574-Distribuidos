from configparser import ConfigParser
import datetime
import socket
import time
import psutil
import threading


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
    """Simple client that get's some system metrics and logs them in our central server
    Ideal for having multiple replicated clients and checking if any of them are behaving out of the ordinary"""

    config = ConfigParser()
    config.read("./config.ini")
    server_alias = config["DEFAULT"]["server_alias"]
    server_port = int(config["DEFAULT"]["server_port"])
    freq = int(config["DEFAULT"]["client_stats_frequency"]) or 10
    is_user_attached = threading.Event()

    def send_query(query, log):
        if not query:
            return
        conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        conn.connect((server_alias, server_port))

        conn.send(f"{query}\n".encode("utf-8"))
        response = conn.recv(1024).rstrip().decode("utf-8")
        if log:
            print(f"SEND -> {query}")
        if log:
            print(f"RECV -> {response}")
        conn.shutdown(socket.SHUT_RDWR)
        conn.close()

    # Separate thread for manual queries
    def manual_query(is_user_attached):
        input()  # Wait for any kind of input, to know there's a user on the other side
        is_user_attached.set()
        while True:
            query = input("QUERY: ")
            send_query(query, True)

    threading.Thread(target=manual_query, args=((is_user_attached,))).start()

    time.sleep(1)
    print(f"START CLIENT -> {datetime.datetime.now().isoformat()}")

    # Tell the world about our stats!
    # Every freq seconds!
    while True:
        stats = get_stats()
        log = not is_user_attached.is_set()
        for (metric_id, metric_value) in stats.items():
            query = f"LOG {metric_id} {metric_value}"
            send_query(query, log)
        time.sleep(freq)


if __name__ == "__main__":
    main()
