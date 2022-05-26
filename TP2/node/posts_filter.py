import zmq
from base_node import BaseNode
import math
import logging
import random


class PostsFilter(BaseNode):
    def __init__(self, *args):
        super().__init__(*args)
        self.collector = self.push_socket("collector")
        self.image_streamer = self.push_socket("image_streamer")

        self.posts_urls = set()
        self.posts_average_score = None
        self.post_max_sentiment_avg = None
        self.score_avg = None

    def work(self, msg):
        if msg.get("post_score_average"):
            self.posts_average_score = msg["post_score_average"]

        if msg.get("permalink") and msg.get("is_student_liked") and msg.get("score"):
            if self.posts_average_score and msg["score"] >= self.posts_average_score:
                self.posts_urls.add(msg["permalink"])
                self.collector.send_json(
                    {
                        "metric_name": "student-liked-posts-sample",
                        "metric_value": random.sample(
                            self.posts_urls, min(len(self.posts_urls), 3)
                        ),
                    }
                )

        if msg.get("url") and msg.get("sentiment_avg"):
            if (
                not self.post_max_sentiment_avg
                or msg["sentiment_avg"] >= self.post_max_sentiment_avg
            ):
                self.post_max_sentiment_avg = msg["sentiment_avg"]
                self.image_streamer.send_json(self.pick_keys(msg, ["url"]))
