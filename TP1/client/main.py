from configparser import ConfigParser
import itertools
import socket
import time
import psutil


def main():
    config = ConfigParser()
    config.read("./config.ini")
    server_alias = config["DEFAULT"]["server_alias"]
    server_port = int(config["DEFAULT"]["server_port"])

    def send_query(query):
        conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        conn.connect((server_alias, server_port))

        conn.send(f"{query}\n".encode("utf-8"))
        response = conn.recv(1024).rstrip().decode("utf-8")
        print(f"SEND {query}")
        print(f"RECV {response}")
        conn.shutdown(socket.SHUT_RDWR)
        conn.close()

    stats = {
        # https://psutil.readthedocs.io/en/latest/
        "cpu_percent": (psutil.cpu_percent(interval=1), 15),
        "cpu_freq_current": (psutil.cpu_freq().current, 2),
        "load_avg_lastminute": (psutil.getloadavg()[0], 3),
        "memory_usage_percent": (psutil.virtual_memory().percent, 24),
        "disk_usage_percent": (psutil.disk_usage("/").percent, 85),
    }
    rounded_stats = {k: round(v[0], 2) for k, v in stats.items()}

    # Let's set up some alerts before logging our metrics
    operations = ["AVG", "MAX"]
    for metric_id, aggregate_op in itertools.product(stats, operations):
        limit = stats[metric_id][1]
        aggregate_secs = 5
        query = f"NEW-ALERT {metric_id} {aggregate_op} {aggregate_secs} {limit}"
        send_query(query)

    # Tell the world about our stats!
    time.sleep(2)
    for (metric_id, metric_value) in rounded_stats.items():
        query = f"LOG {metric_id} {metric_value}"
        send_query(query)

    # We now have lots of metrics, let's wait for them to arrive and then query them
    time.sleep(2)
    for metric_id, aggregate_op in itertools.product(stats, operations):
        aggregate_secs = 5
        query = f"QUERY {metric_id} {aggregate_op} {aggregate_secs}"
        send_query(query)


if __name__ == "__main__":
    main()
