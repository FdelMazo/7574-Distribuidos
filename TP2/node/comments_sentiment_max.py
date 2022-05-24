import zmq
from base_node import BaseNode
import math
import logging


class CommentsSentimentMax(BaseNode):
    def __init__(self, *args):
        super().__init__(*args)
        self.post_max_sentiment_avg = None
        self.post_max_sentiment_id = None

    def work(self, msg):
        if not self.post_max_sentiment_avg or msg["avg"] > self.post_max_sentiment_avg:
            self.post_max_sentiment_avg = msg["avg"]
            self.post_max_sentiment_id = msg["id"]
            logging.info(
                f"Post with id {msg['id']} has average sentiment {msg['avg']:.2f}"
            )

    def shutdown(self):
        self.comments_transformer.setsockopt(zmq.LINGER, 0)
        self.comments_transformer.close()
        super().shutdown()
