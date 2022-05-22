import logging
import signal
from configparser import ConfigParser
from server import Server


def main():
    logging.basicConfig(
        format="%(asctime)s %(levelname)-8s %(message)s",
        level=logging.DEBUG,
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    config = ConfigParser()
    config.read("./config.ini")

    port = int(config["NETWORK"]["server_port"])
    posts_worker_host = (
        config["NETWORK"]["posts_worker_hostname"],
        int(config["NETWORK"]["posts_worker_port"]),
    )

    server = Server(port, posts_worker_host)

    def shutdown():
        logging.info("Shutting Down")
        server.shutdown()

    signal.signal(signal.SIGTERM, lambda _n, _f: shutdown())
    server.run()


if __name__ == "__main__":
    main()
