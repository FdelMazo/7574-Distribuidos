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
        # On one branch of the dag: send the score to an averager to calculate the post
        # score average
        self.posts_averager.send_json(self.pick_keys(msg, ["score"]))

        # On the other branch of the dag: send the post metadata we want to the joiner,
        # which will serve as a kind of database for the system
        self.joiner.send_json(
            self.pick_keys(msg, ["id", "score", "permalink", "url"])
        )
