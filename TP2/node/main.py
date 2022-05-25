import logging
import signal
from configparser import ConfigParser
from node_factory import NodeFactory
import os


def main():
    """
    A little setup for any Node class, which are all classes that inherit from BaseNode
    We decide which Node to instantiate based on the 'NODE_TYPE' env var and checking it
    against the NodeFactory dictionary (a {node_type_name: node_type_class} dict)
    """
    config = ConfigParser()
    config.read("./config.ini")

    logging.basicConfig(
        format="%(message)s",
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
    node.run()


if __name__ == "__main__":
    main()
