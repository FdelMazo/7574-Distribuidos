from base_node import BaseNode
import logging

class Source(BaseNode):
    """
    The source node is the very first node in the DAG serving as the starting point
    of everything we want to process. It's simply a dispatcher that pushes a message
    according to it's type

    Even though this node doesn't keep any kind of state and we can replicate it, it's
    cleaner to keep a single source node and if we were to need more workers we can
    simply replicate the PostsWorker or CommentsWorker
    """

    def __init__(self, *args):
        super().__init__(*args)
        self.posts_worker = self.push_socket("posts_worker")
        self.comments_worker = self.push_socket("comments_worker")
        self.collector = self.push_socket("collector")

        # This flag is just a safety measure. We already know that if we get an EOF
        # message we won't receive any new messages. We keep it any way.
        self.discard = False

    def work(self, msg):
        if msg["type"] == "EOF":
            logging.info(f"Got EOF => Stop all means of production")
            self.collector.send_json(msg)
            self.discard = True

        if self.discard:
            return

        if msg["type"] == "post":
            self.posts_worker.send_json(msg)
        elif msg["type"] == "comment":
            self.comments_worker.send_json(msg)
