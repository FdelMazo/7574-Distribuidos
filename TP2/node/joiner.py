from base_node import BaseNode


class Joiner(BaseNode):
    """
    The joiner node can be considered the most important node in the whole DAG.
    (Only maybe second to the filterer)

    It serves us as the 'database' of the DAG, receiving posts with metadata from
    different parts of the DAG and joining them together before sending them to the
    filterer which will sort out the rest of the post journey

    This node can't be replicated!
    """

    def __init__(self, *args):
        super().__init__(*args)
        # Sockets
        self.filterer = self.push_socket("filterer")

        # State
        self.posts = {}

    def work(self, msg):
        # Update the posts dictionary with whatever we receive, and then push it to the 
        # filterer
        self.posts.setdefault(msg["id"], {}).update(
            {k: v for k, v in msg.items() if k != "id"}
        )
        self.filterer.send_json(self.posts[msg["id"]])
