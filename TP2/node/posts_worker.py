import zmq
from base_node import BaseNode


class PostsWorker(BaseNode):
    def __init__(self, *args):
        super().__init__(*args)
        posts_collector_host = self.get_host("posts_collector")
        self.posts_collector = self.context.socket(zmq.PUSH)
        self.posts_collector.connect(
            f"tcp://{posts_collector_host[0]}:{posts_collector_host[1]}"
        )

    def work(self, msg):
        keys_to_keep = ["id", "score"]
        filtered_msg = {k: v for k, v in msg.items() if k in keys_to_keep}
        self.posts_collector.send_json(filtered_msg)

    def shutdown(self):
        self.posts_collector.setsockopt(zmq.LINGER, 0)
        self.posts_collector.close()
        super().shutdown()
