from comments_worker import CommentsWorker
from comments_sentiment_worker import CommentsSentimentWorker
from comments_sentiment_max import CommentsSentimentMax
from posts_worker import PostsWorker
from collector import Collector
from source import Source

NodeFactory = {
    "source": Source,
    "posts_worker": PostsWorker,
    "collector": Collector,
    "comments_worker": CommentsWorker,
    "comments_sentiment_worker": CommentsSentimentWorker,
    "comments_sentiment_max": CommentsSentimentMax,
}
