import zmq
from base_node import BaseNode
import re
import logging


class CommentsSentimentWorker(BaseNode):
    def __init__(self, *args):
        super().__init__(*args)
        self.posts_sentiments_sum = {}
        self.posts_sentiments_count = {}
        comments_sentiment_max_host = self.get_host("comments_sentiment_max")
        self.comments_sentiment_max = self.context.socket(zmq.PUSH)
        self.comments_sentiment_max.connect(
            f"tcp://{comments_sentiment_max_host[0]}:{comments_sentiment_max_host[1]}"
        )

    def work(self, msg):
        self.posts_sentiments_count[msg["post_id"]] = (
            self.posts_sentiments_count.get(msg["post_id"], 0) + 1
        )
        self.posts_sentiments_sum[msg["post_id"]] = (
            self.posts_sentiments_count.get(msg["post_id"], 0) + msg["sentiment"]
        )
        avg = (
            self.posts_sentiments_sum[msg["post_id"]]
            / self.posts_sentiments_count[msg["post_id"]]
        )
        self.comments_sentiment_max.send_json({"id": msg["post_id"], "avg": avg})

    def shutdown(self):
        self.comments_transformer.setsockopt(zmq.LINGER, 0)
        self.comments_transformer.close()
        super().shutdown()
