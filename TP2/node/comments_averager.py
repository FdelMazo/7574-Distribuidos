import zmq
from base_node import BaseNode
import re
import logging


class CommentsAverager(BaseNode):
    def __init__(self, *args):
        super().__init__(*args)
        self.joiner = self.push_socket("joiner")
        self.posts_sentiments_sum = {}
        self.posts_sentiments_count = {}

    def work(self, msg):
        try:
            sentiment = float(msg["sentiment"])
        except ValueError:
            return

        self.posts_sentiments_count[msg["post_id"]] = (
            self.posts_sentiments_count.get(msg["post_id"], 0) + 1
        )
        self.posts_sentiments_sum[msg["post_id"]] = (
            self.posts_sentiments_sum.get(msg["post_id"], 0) + sentiment
        )
        avg = (
            self.posts_sentiments_sum[msg["post_id"]]
            / self.posts_sentiments_count[msg["post_id"]]
        )
        self.joiner.send_json({**msg, "sentiment_avg": avg})
