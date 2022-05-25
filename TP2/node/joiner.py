import zmq
import logging
from base_node import BaseNode


class Joiner(BaseNode):
    def __init__(self, *args):
        super().__init__(*args)
        self.posts = {}
        self.posts_max_sentiment = self.push_socket("posts_max_sentiment")

    def work(self, msg):
        if msg["type"] == "post":
            avoid = ["type", "id"]
            self.posts.setdefault(msg["id"], {}).update(
                {k: v for k, v in msg.items() if k not in avoid}
            )

        elif msg["type"] == "comment":
            avoid = ["type", "post_id"]
            self.posts.setdefault(msg["post_id"], {}).update(
                {k: v for k, v in msg.items() if k not in avoid}
            )
            if self.posts[msg["post_id"]].get("url"):
                self.posts_max_sentiment.send_json(self.posts[msg["post_id"]])
