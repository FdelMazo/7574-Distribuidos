import zmq
from base_node import BaseNode
import re
import logging

RE_COMMENT_TO_POST = re.compile(r"reddit\.com\/r\/\w*\/comments\/(\w*)\/")
COLLEGE_KEYWORDS = ["university", "college", "student", "teacher", "professor"]


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

    def work(self, msg):
        keys_to_keep = ["type", "sentiment"]
        filtered_msg = {k: v for k, v in msg.items() if k in keys_to_keep}

        # We can deduce the post_id from a given comment's permalink
        filtered_msg["post_id"] = RE_COMMENT_TO_POST.search(msg["permalink"]).group(1)

        # We create a simple boolean that indicates if the comment is student-related
        filtered_msg["is_student_liked"] = any(
            [college.lower() in msg["body"].lower() for college in COLLEGE_KEYWORDS]
        )

        # We send everything to the next node in the DAG: the comments_averager
        self.comments_averager.send_json(filtered_msg)
