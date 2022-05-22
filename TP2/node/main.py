import logging
import signal
from configparser import ConfigParser
from posts_worker import PostsWorker
from posts_collector import PostsCollector
from source import Source
import os


NodeFactory = {
    "source": Source,
    "posts_worker": PostsWorker,
    "posts_collector": PostsCollector,
}


def main():
    config = ConfigParser()
    config.read("./config.ini")

    logging.basicConfig(
        format="%(asctime)s %(levelname)-8s %(message)s",
        level=config["LOGGING"]["level"],
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    node_type = os.environ.get("NODE_TYPE")
    if not node_type:
        return

    network_config = config["NETWORK"]
    node = NodeFactory[node_type](node_type, network_config)

    def shutdown():
        logging.info("Shutting Down")
        node.shutdown()

    signal.signal(signal.SIGTERM, lambda _n, _f: shutdown())
    node.start()


if __name__ == "__main__":
    main()
