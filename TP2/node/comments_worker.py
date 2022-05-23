import zmq
from base_node import BaseNode
import re
import logging

RE_COMMENT_TO_POST = re.compile(r"reddit\.com\/r\/\w*\/comments\/(\w*)\/")
COLLEGE_KEYWORDS = ['university', 'college', 'student', 'teacher', 'professor']

class CommentsWorker(BaseNode):
    def __init__(self, *args):
        super().__init__(*args)

    def work(self, msg):
        # keys_to_keep = ["sentiment", "permalink"]
        # filtered_msg = {k: v for k, v in msg.items() if k in keys_to_keep}
        to_push = {}
        try:
            to_push["sentiment"] = float(msg["sentiment"])
        except ValueError:
            return

        to_push["post_id"] = RE_COMMENT_TO_POST.search(msg["permalink"]).group(1)
        to_push["is_college"] = any([college.lower() in msg['body'].lower() for college in COLLEGE_KEYWORDS])
        logging.info(to_push)

    def shutdown(self):
        self.comments_transformer.setsockopt(zmq.LINGER, 0)
        self.comments_transformer.close()
        super().shutdown()
