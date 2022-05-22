import logging
from base_node import BaseNode


class PostsWorker(BaseNode):
    def __init__(self, *args):
        super().__init__(*args)
        self.posts_n = 0
        self.posts_scores_sum = 0
    
    def work(self, msg):
        keys_to_keep = ['id', 'score']
        filtered_msg = {k: v for k, v in msg.items() if k in keys_to_keep}
        self.posts_n += 1
        self.posts_scores_sum += int(filtered_msg['score'])
        logging.info(self.posts_scores_sum / self.posts_n)

