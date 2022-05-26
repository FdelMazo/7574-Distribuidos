from base_node import BaseNode
import random


class PostsFilter(BaseNode):
    """
    The PostsFilter node receives posts with different metadata and only pushes forward
    those that meet different criteria. 

    The current rules that it handles are:
    - Keep the student-liked posts which score is above average
    - Keep the post with the highest average sentiment

    This node keeps state and thus cannot be replicated
    """
    def __init__(self, *args):
        super().__init__(*args)
        # Sockets
        self.collector = self.push_socket("collector")
        self.image_streamer = self.push_socket("image_streamer")

        # State
        self.posts_urls = set()
        self.posts_average_score = None
        self.post_max_sentiment_avg = None

    def work(self, msg):
        # If we receive a student-liked post with both permalink and score, we send a
        # metric to the user consisting of a n-sample of the post urls with score above
        # average
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

        # If we receive a post with sentiment_avg and url, we push forward the url to
        # the image_streamer if it's the max sentiment_avg we encountered
        if msg.get("url") and msg.get("sentiment_avg"):
            if (
                not self.post_max_sentiment_avg
                or msg["sentiment_avg"] >= self.post_max_sentiment_avg
            ):
                # keep track of the highest sentiment_avg
                self.post_max_sentiment_avg = msg["sentiment_avg"]
                # send the url
                self.image_streamer.send_json(self.pick_keys(msg, ["url"]))

        # If we receive a post_score_average, we set it, to have it as a threshold
        if msg.get("post_score_average"):
            self.posts_average_score = msg["post_score_average"]
