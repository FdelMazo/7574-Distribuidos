from base_node import BaseNode


class CommentsAverager(BaseNode):
    """
    REPENSAR ESTO
    The CommentsAverager averages every post comments according to their sentiment,
    comment from the source node, filters out the attributes we don't need, processes
    some attributes, and sends everything to the next node in the DAG

    This node keeps track of the sum and count of each post comments, and as such can't
    be replicated. There must only be one CommentsAverager node in the whole DAG
    """

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
