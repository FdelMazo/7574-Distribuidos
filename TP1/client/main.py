from configparser import ConfigParser
import socket
import psutil


def main():
    config = ConfigParser()
    config.read("./config.ini")
    server_alias = config["DEFAULT"]["server_alias"]
    server_port = int(config["DEFAULT"]["server_port"])

    stats = {
        # https://psutil.readthedocs.io/en/latest/
        "cpu_percent": psutil.cpu_percent(interval=1),
        "cpu_freq_current": psutil.cpu_freq().current,
        "load_avg_lastminute": psutil.getloadavg()[0],
        "memory_usage_percent": psutil.virtual_memory().percent,
        "disk_usage_percent": psutil.disk_usage("/").percent,
    }
    rounded_stats = {k: round(v, 2) for k, v in stats.items()}

    for (metric_id, metric_value) in rounded_stats.items():
        conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        conn.connect((server_alias, server_port))

        query = f"LOG {metric_id} {metric_value}\n"
        conn.send(query.encode("utf-8"))

        response = conn.recv(1024).rstrip().decode("utf-8")
        status_code = response.split()[0]
        if status_code != "200":
            print(f"Error while sending metric {metric_id}: {response}")

        conn.shutdown(socket.SHUT_RDWR)
        conn.close()


if __name__ == "__main__":
    main()
