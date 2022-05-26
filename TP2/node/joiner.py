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
        self.posts.setdefault(msg["id"], {}).update(
            {k: v for k, v in msg.items() if k != 'id'}
        )
        self.posts_filter.send_json(self.posts[msg["id"]])
