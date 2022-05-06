import logging
import signal
from configparser import ConfigParser
from server import Server
from alert_monitor import AlertMonitor
from metrics_manager import MetricsManager
from file_manager import FileManager
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
    alert_freq = int(config["DEFAULT"]["server_alert_frequency"]) or 60

    process_manager_lock = multiprocessing.Manager().Lock()
    alerts = multiprocessing.Manager().dict()
    alerts_lock = multiprocessing.Manager().Lock()
    file_manager = FileManager(process_manager_lock)
    metrics_manager = MetricsManager(file_manager)

    alert_monitor = AlertMonitor(metrics_manager, alerts, alerts_lock, alert_freq)
    alert_monitor_process = multiprocessing.Process(target=alert_monitor.run)

    server = Server(port, metrics_manager, alert_monitor)

    def shutdown():
        logging.info("Shutting Down")
        server.shutdown()
        alert_monitor.shutdown()
        alert_monitor_process.join()

    signal.signal(signal.SIGTERM, lambda _n, _f: shutdown())
    alert_monitor_process.start()
    server.run()


if __name__ == "__main__":
    main()
