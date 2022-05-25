import zmq
import logging
from base_node import BaseNode


class PostsAverager(BaseNode):
    def __init__(self, *args):
        super().__init__(*args)
        self.posts_filter = self.push_socket("posts_filter")
        self.collector = self.push_socket("collector")
        self.posts_score_sum = 0
        self.posts_n = 0

    def work(self, msg):
        self.posts_n += 1
        self.posts_score_sum += int(msg["score"])
        self.posts_filter.send_json(
            {"post_score_average": self.posts_score_sum / self.posts_n}
        )
        self.collector.send_json(
            {
                "metric_name": "post_score_average",
                "metric_value": f"{self.posts_score_sum / self.posts_n:.2f}",
            }
        )
