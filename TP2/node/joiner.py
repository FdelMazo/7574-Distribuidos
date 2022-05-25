from base_node import BaseNode


class Joiner(BaseNode):
    """
    The joiner node can be considered the most important node in the whole DAG.
    It serves us as the 'database' of the DAG, receiving both posts and comments, and
    linking them together so that we can then later process them over aggregated comment
    attributes while not loosing the post original attributes.

    This node can't be replicated!
    """

    def __init__(self, *args):
        super().__init__(*args)
        self.posts = {}
        self.posts_max_sentiment = self.push_socket("posts_max_sentiment")
        self.posts_filter = self.push_socket("posts_filter")

    def work(self, msg):
        if msg["type"] == "post":
            avoid = ["type", "id"]
            self.posts.setdefault(msg["id"], {}).update(
                {k: v for k, v in msg.items() if k not in avoid}
            )
            post = self.posts[msg["id"]]

        elif msg["type"] == "comment":
            avoid = ["type", "post_id"]
            if not msg["is_student_liked"] and self.posts.get(msg["post_id"], {}).get(
                "is_student_liked"
            ):
                avoid.append("is_student_liked")

            self.posts.setdefault(msg["post_id"], {}).update(
                {k: v for k, v in msg.items() if k not in avoid}
            )
            post = self.posts[msg["post_id"]]

        if post.get("url") and post.get("sentiment_avg"):
            self.posts_max_sentiment.send_json(post)

        if post.get("permalink") and post.get("is_student_liked"):
            self.posts_filter.send_json(post)
