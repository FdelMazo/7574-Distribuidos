from base_node import BaseNode


class ScoreAverager(BaseNode):
    """
    The ScoreAverager receives posts and keeps track of the sum of scores and the number
    of posts, thus easily calculating the average score and then sending that metric to
    the nodes that need them
    """

    def __init__(self, *args):
        super().__init__(*args)
        # Sockets
        self.filterer = self.push_socket("filterer")
        self.collector = self.push_socket("collector")

        # State
        self.posts_score_sum = 0
        self.posts_n = 0

    def work(self, msg):
        self.posts_n += 1
        self.posts_score_sum += int(msg["score"])

        # The posts filterer needs to know the average, to filter out posts that are
        # below that threshold
        self.filterer.send_json(
            {"post_score_average": self.posts_score_sum / self.posts_n}
        )

        # The posts score average is also a metric itself that we want to send to the
        # user, thus we send it to the collector
        self.collector.send_json(
            {
                "metric_name": "post_score_average",
                "metric_value": f"{self.posts_score_sum / self.posts_n:.2f}",
            }
        )
