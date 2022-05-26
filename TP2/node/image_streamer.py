from base_node import BaseNode
import requests
import base64


class ImageStreamer(BaseNode):
    """
    The image streamer simply receives a meme url, encodes it and sends it to the user
    (by passing it to the collector)
    """

    def __init__(self, *args):
        super().__init__(*args)
        self.collector = self.push_socket("collector")

    def work(self, msg):
        response = requests.get(msg["url"])
        
        # The encoding consists of base64 encoding the image bytes, and then converting
        # them into an ascii string, to make them transportable through a json
        # (i.e, one can't send a b'' string through a json, only a simple '' string)
        b64 = base64.b64encode(response.content)
        asciistr = b64.decode("ascii")

        self.collector.send_json(
            {
                "metric_name": "high-sentiment-meme",
                "metric_encoded": True,
                "metric_value": asciistr,
            }
        )
