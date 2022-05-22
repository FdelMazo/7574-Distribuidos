import logging
import signal
from configparser import ConfigParser
from server import Server


def main():
    config = ConfigParser()
    config.read("./config.ini")

    logging.basicConfig(
        format="%(asctime)s %(levelname)-8s %(message)s",
        level=config["LOGGING"]["level"],
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    network_config = config["NETWORK"]
    server = Server(network_config)

    def shutdown():
        logging.info("Shutting Down")
        server.shutdown()

    signal.signal(signal.SIGTERM, lambda _n, _f: shutdown())
    server.run()


if __name__ == "__main__":
    main()
