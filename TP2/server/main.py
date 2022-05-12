import logging
import signal
from configparser import ConfigParser
from server import Server
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
    server = Server(port)

    def shutdown():
        logging.info("Shutting Down")
        server.shutdown()

    signal.signal(signal.SIGTERM, lambda _n, _f: shutdown())
    server.run()


if __name__ == "__main__":
    main()
