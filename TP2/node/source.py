import logging
import zmq
from base_node import BaseNode


class Source(BaseNode):
    def __init__(self, *args):
        super().__init__(*args)
        self.posts_worker = self.push_socket("posts_worker")
        self.comments_worker = self.push_socket("comments_worker")

    def work(self, msg):
        if msg["type"] == "post":
            self.posts_worker.send_json(msg)
        elif msg["type"] == "comment":
            self.comments_worker.send_json(msg)
