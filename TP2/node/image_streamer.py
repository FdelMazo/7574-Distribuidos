import zmq
from base_node import BaseNode
import math
import logging
import requests
import base64


class ImageStreamer(BaseNode):
    def __init__(self, *args):
        super().__init__(*args)
        self.collector = self.push_socket("collector")

    def work(self, msg):
        response = requests.get(msg["url"])
        b64 = base64.b64encode(response.content)
        asciistr = b64.decode("ascii")

        self.collector.send_json(
            {
                "metric_name": "high-sentiment-meme",
                "metric_encoded": True,
                "metric_value": asciistr,
            }
        )
