import logging
import zmq
from base_node import BaseNode


class PostsWorker(BaseNode):
    def __init__(self, *args):
        super().__init__(*args)
        self.posts_averager = self.push_socket("posts_averager")
        self.joiner = self.push_socket("joiner")

    def work(self, msg):
        fileterd_keys = ["type", "id", "score", "permalink", "url"]
        self.posts_averager.send_json({"score": msg["score"]})
        self.joiner.send_json({k: v for k, v in msg.items() if k in fileterd_keys})
