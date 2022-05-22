import zmq
import logging
from base_node import BaseNode
from base_sink import BaseSink


class PostsCollector(BaseSink):
    def __init__(self, *args):
        super().__init__(*args)
        self.posts_score_sum = 0
        self.posts_n = 0

    def work(self, msg):
        self.posts_n += 1
        self.posts_score_sum += int(msg["score"])

    def reply(self, msg):
        if not self.posts_n:
            return str(0)
        return f"{self.posts_score_sum / self.posts_n:.4f}"
