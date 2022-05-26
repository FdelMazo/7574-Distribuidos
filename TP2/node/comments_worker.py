from base_node import BaseNode
import re

RE_COMMENT_TO_POST = re.compile(r"reddit\.com\/r\/\w*\/comments\/(\w*)\/")


class CommentsWorker(BaseNode):
    """
    The CommentsWorker is the first node that processes comments. It receives a comment
    from the source node and then sends the neccessary attributes to the next nodes in
    the DAG

    As this node doesn't keep any kind of state, we can replicate it as much as we want,
    if we were to see that we need more comment workers
    """

    def __init__(self, *args):
        super().__init__(*args)
        self.comments_averager = self.push_socket("comments_averager")
        self.student_decider = self.push_socket("student_decider")

    def work(self, msg):
        # We can deduce the post_id from a given comment's permalink!
        # Keep in mind we are overwriting the 'id' attribute that previously referred to
        # the comments id and now refers to the post id, as we don't need to singularly
        # identify particular comments throughout the whole file
        msg["id"] = RE_COMMENT_TO_POST.search(msg["permalink"]).group(1)

        # We send the sentiment to the comments_averager
        self.comments_averager.send_json(self.pick_keys(msg, ["id", "sentiment"]))
        # We send the body to the decider that checks if it contains any relevant word
        # for our analysis
        self.student_decider.send_json(self.pick_keys(msg, ["id", "body"]))
