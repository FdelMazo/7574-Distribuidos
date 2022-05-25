from comments_worker import CommentsWorker
from comments_averager import CommentsAverager
from posts_max_sentiment import PostsMaxSentiment
from image_streamer import ImageStreamer
from posts_worker import PostsWorker
from posts_averager import PostsAverager
from posts_filter import PostsFilter
from source import Source
from joiner import Joiner

NodeFactory = {
    "source": Source,
    "joiner": Joiner,
    "image_streamer": ImageStreamer,
    "posts_worker": PostsWorker,
    "posts_averager": PostsAverager,
    "posts_filter": PostsFilter,
    "comments_worker": CommentsWorker,
    "comments_averager": CommentsAverager,
    "posts_max_sentiment": PostsMaxSentiment,
}
