from base_node import BaseNode


class PostsWorker(BaseNode):
    """
    The PostsWorker is the first node that processes posts. It receives a post from
    the source node, filters out the attributes we don't need at all (thus reducing the
    payload size) and sends it to the next nodes in the DAG
    
    As this node doesn't keep any kind of state, we can replicate it as much as we want,
    if we were to see that we need more post workers
    """
    def __init__(self, *args):
        super().__init__(*args)
        self.posts_averager = self.push_socket("posts_averager")
        self.joiner = self.push_socket("joiner")

    def work(self, msg):
        fileterd_keys = ["type", "id", "score", "permalink", "url"]

        # The posts_averager only needs the post score
        self.posts_averager.send_json({"score": msg["score"]})
        # The joiner needs more attributes to join the posts and the comments
        self.joiner.send_json({k: v for k, v in msg.items() if k in fileterd_keys})
