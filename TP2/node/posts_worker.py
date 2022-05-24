import zmq
from base_node import BaseNode


class PostsWorker(BaseNode):
    def __init__(self, *args):
        super().__init__(*args)
        collector_host = self.get_host("collector")
        self.collector = self.context.socket(zmq.PUSH)
        self.collector.connect(
            f"tcp://{collector_host[0]}:{collector_host[1]}"
        )

    def work(self, msg):
        keys_to_keep = ["id", "score"]
        filtered_msg = {k: v for k, v in msg.items() if k in keys_to_keep}
        self.collector.send_json(filtered_msg)

    def shutdown(self):
        self.collector.setsockopt(zmq.LINGER, 0)
        self.collector.close()
        super().shutdown()
