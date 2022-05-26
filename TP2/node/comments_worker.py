import zmq
from base_node import BaseNode
import re
import logging

RE_COMMENT_TO_POST = re.compile(r"reddit\.com\/r\/\w*\/comments\/(\w*)\/")


class CommentsWorker(BaseNode):
    """
    The CommentsWorker is the first node that processes comments. It receives a
    comment from the source node, filters out the attributes we don't need, processes
    some attributes, and sends everything to the next node in the DAG

    As this node doesn't keep any kind of state, we can replicate it as much as we want,
    if we were to see that we need more comment workers
    """

    def __init__(self, *args):
        super().__init__(*args)
        self.comments_averager = self.push_socket("comments_averager")
        self.student_decider = self.push_socket("student_decider")

    def work(self, msg):
        # We can deduce the post_id from a given comment's permalink
        
        # Keep in mind we are overwriting the 'id' attribute that previously referred to
        # the comments id and now refers to the post id, as we don't need to singularly
        # identify particular comments throughout the whole file
        msg["id"] = RE_COMMENT_TO_POST.search(msg["permalink"]).group(1)
        self.comments_averager.send_json(self.pick_keys(msg, ["id", "sentiment"]))
        self.student_decider.send_json(self.pick_keys(msg, ["id", "body"]))

        # keys_to_keep = ["type", "sentiment"]
        # filtered_msg = {k: v for k, v in msg.items() if k in keys_to_keep}

        # # We send everything to the next node in the DAG: the comments_averager
        # self.filter.send_json(filtered_msg)
