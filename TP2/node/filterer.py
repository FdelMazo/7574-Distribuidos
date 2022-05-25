import zmq
import logging
from base_node import BaseNode


class Joiner(BaseNode):
    def __init__(self, *args):
        super().__init__(*args)
        self.filter_metrics = {}

    def work(self, msg):
        if msg["type"] == "filter_metric":
            self.posts.setdefault(msg["filter_metric"], {}).update(msg)

        if msg["type"] == "filter_task":
            self.posts.setdefault(msg["filter_metric"], {}).update(msg)

        elif msg["type"] == "comment":
            avoid = ["type", "post_id"]
            self.posts.setdefault(msg["post_id"], {}).update(
                {k: v for k, v in msg.items() if k not in avoid}
            )
