import logging
import zmq
from base_node import BaseNode


class Source(BaseNode):
    def __init__(self, *args):
        super().__init__(*args)
        posts_worker_host = self.get_host("posts_worker")
        self.posts_worker = self.context.socket(zmq.PUSH)
        self.posts_worker.connect(
            f"tcp://{posts_worker_host[0]}:{posts_worker_host[1]}"
        )

    def work(self, msg):
        if msg["type"] == "post":
            self.posts_worker.send_json(msg)


    def shutdown(self):
        self.posts_worker.setsockopt(zmq.LINGER, 0)
        self.posts_worker.close()
        super().shutdown()
