import logging
import signal
from configparser import ConfigParser
from posts_worker import PostsWorker
import os


NodeFactory = {
    "posts_worker": PostsWorker,
}

def main():
    logging.basicConfig(
        format="%(asctime)s %(levelname)-8s %(message)s",
        level=logging.DEBUG,
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    config = ConfigParser()
    config.read("./config.ini")

    node_type = os.environ.get("NODE_TYPE")
    if not node_type:
        return

    network_config = config["NETWORK"]
    port = int(network_config[f"{node_type}_port"])
    node = NodeFactory[node_type](port, network_config)

    def shutdown():
        logging.info("Shutting Down")
        node.shutdown()

    signal.signal(signal.SIGTERM, lambda _n, _f: shutdown())
    node.run()


if __name__ == "__main__":
    main()
