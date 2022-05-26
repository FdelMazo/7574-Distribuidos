from base_node import BaseNode


class SentimentAverager(BaseNode):
    """
    The SentimentAverager receives comments from the CommentsWorker, aggregates them by
    their post id and then sends the post with the sentiment_avg to the joiner

    This node keeps track of the sum and count of each post comments, and as such can't
    be replicated. There must only be one SentimentAverager node in the whole DAG
    """

    def __init__(self, *args):
        super().__init__(*args)
        # Sockets
        self.joiner = self.push_socket("joiner")

        # State
        self.posts_sentiments_sum = {}
        self.posts_sentiments_count = {}

    def work(self, msg):
        # We discard comments with no sentiment
        if msg["sentiment"] is None:
            return

        post_id = msg["id"]
        sentiment = float(msg["sentiment"])
        self.posts_sentiments_count[post_id] = (
            self.posts_sentiments_count.get(post_id, 0) + 1
        )

        self.posts_sentiments_sum[post_id] = (
            self.posts_sentiments_sum.get(post_id, 0) + sentiment
        )

        msg["sentiment_avg"] = (
            self.posts_sentiments_sum[post_id] / self.posts_sentiments_count[post_id]
        )
        self.joiner.send_json(self.pick_keys(msg, ["id", "sentiment_avg"]))
