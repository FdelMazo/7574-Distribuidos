import zmq
from base_node import BaseNode
import math
import logging
import random


class PostsFilter(BaseNode):
    def __init__(self, *args):
        super().__init__(*args)
        self.collector = self.push_socket("collector")
        self.posts_urls = set()
        self.posts_average_score = None

    def work(self, msg):
        if msg.get("post_score_average"):
            self.posts_average_score = msg["post_score_average"]

        elif (
            self.posts_average_score
            and msg.get("permalink")
            and float(msg.get("score", 0)) > self.posts_average_score
        ):
            if msg["permalink"] in self.posts_urls:
                return

            self.posts_urls.add(msg["permalink"])
            self.collector.send_json(
                {
                    "metric_name": "student-liked-posts-sample",
                    "metric_value": random.sample(
                        self.posts_urls, min(len(self.posts_urls), 3)
                    ),
                }
            )
