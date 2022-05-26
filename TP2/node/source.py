from base_node import BaseNode


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

    def work(self, msg):
        if msg["type"] == "post":
            self.posts_worker.send_json(msg)
        elif msg["type"] == "comment":
            self.comments_worker.send_json(msg)
