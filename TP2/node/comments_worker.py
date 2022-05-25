import zmq
from base_node import BaseNode
import re
import logging

RE_COMMENT_TO_POST = re.compile(r"reddit\.com\/r\/\w*\/comments\/(\w*)\/")
COLLEGE_KEYWORDS = ["university", "college", "student", "teacher", "professor"]


class CommentsWorker(BaseNode):
    def __init__(self, *args):
        super().__init__(*args)
        self.comments_averager = self.push_socket("comments_averager")

    def work(self, msg):
        keys_to_keep = ["type", "sentiment"]
        filtered_msg = {k: v for k, v in msg.items() if k in keys_to_keep}
        filtered_msg["post_id"] = RE_COMMENT_TO_POST.search(msg["permalink"]).group(1)
        filtered_msg["is_college"] = any(
            [college.lower() in msg["body"].lower() for college in COLLEGE_KEYWORDS]
        )
        self.comments_averager.send_json(filtered_msg)
