from base_node import BaseNode

STUDENT_KEYWORDS = ["university", "college", "student", "teacher", "professor"]


class StudentDecider(BaseNode):
    """
    The StudentDecider checks if a comment contains any keywords relevant to our
    search, then sets up a boolean attribute to track this and sends it off to the post
    joiner

    It currently only searches for student-related keywords.

    This node keeps track of the sum and count of each post comments, and as such can't
    be replicated. There must only be one CommentsAverager node in the whole DAG
    """

    def __init__(self, *args):
        super().__init__(*args)
        # Sockets
        self.joiner = self.push_socket("joiner")

        # State
        # We could also not keep any kind of state in this node (making it replicable)
        # and just send a post to the joiner every time we encounter a relevant comment.
        # However, that would increment the traffic that the joiner receives and that's
        # a trade-off we don't want to make
        self.student_posts = set()

    def work(self, msg):
        is_student = any(
            [student.lower() in msg["body"].lower() for student in STUDENT_KEYWORDS]
        )

        # We only want to send each post once, so we only push forward the posts that we
        # didn't yet encounter
        if msg["id"] not in self.student_posts and is_student:
            self.student_posts.add(msg["id"])
            msg["is_student_liked"] = True
            self.joiner.send_json(self.pick_keys(msg, ["id", "is_student_liked"]))
