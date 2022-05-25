import zmq
from base_node import BaseNode


class PostsMaxSentiment(BaseNode):
    def __init__(self, *args):
        super().__init__(*args)
        self.image_streamer = self.push_socket("image_streamer")
        self.post_max_sentiment_avg = None

    def work(self, msg):
        if (
            not self.post_max_sentiment_avg
            or msg["sentiment_avg"] >= self.post_max_sentiment_avg
        ):
            self.post_max_sentiment_avg = msg["sentiment_avg"]
            self.image_streamer.send_json(msg)
