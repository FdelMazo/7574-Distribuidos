import logging
import signal
from configparser import ConfigParser
from server import Server
from alert_monitor import AlertMonitor
import multiprocessing


def main():
    logging.basicConfig(
        format="%(asctime)s %(levelname)-8s %(message)s",
        level=logging.DEBUG,
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    config = ConfigParser()
    config.read("./config.ini")

    port = int(config["DEFAULT"]["server_port"])
    listen_backlog = int(config["DEFAULT"]["server_listen_backlog"])

    server = Server(port, listen_backlog)
    server_process = multiprocessing.Process(target=server.run)

    alert_monitor = AlertMonitor()
    alert_monitor_process = multiprocessing.Process(target=alert_monitor.run)

    def shutdown():
        logging.info("Shutting Down")
        server.shutdown()
        alert_monitor.shutdown()
        server_process.join()
        alert_monitor_process.join()

    signal.signal(signal.SIGTERM, lambda _n, _f: shutdown())

    server_process.start()
    alert_monitor_process.start()


if __name__ == "__main__":
    main()
