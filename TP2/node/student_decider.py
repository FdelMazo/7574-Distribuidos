from base_node import BaseNode

COLLEGE_KEYWORDS = ["university", "college", "student", "teacher", "professor"]


class StudentDecider(BaseNode):
    """
    REPENSAR ESTO -> Llamarlo sentiment_averager y score_averager
    The CommentsAverager averages every post comments according to their sentiment,
    comment from the source node, filters out the attributes we don't need, processes
    some attributes, and sends everything to the next node in the DAG

    This node keeps track of the sum and count of each post comments, and as such can't
    be replicated. There must only be one CommentsAverager node in the whole DAG
    """

    def __init__(self, *args):
        super().__init__(*args)
        self.joiner = self.push_socket("joiner")
        
        # aclarar que podríamos no tener estado...
        self.student_posts = set()

    def work(self, msg):
        is_student = any(
            [college.lower() in msg["body"].lower() for college in COLLEGE_KEYWORDS]
        )
        if msg["post_id"] not in self.student_posts and is_student:
            self.student_posts.add(msg["post_id"])
            self.joiner.send_json({"id": msg["post_id"], "is_student_liked": True})
