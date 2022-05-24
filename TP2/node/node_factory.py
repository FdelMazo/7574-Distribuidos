from comments_worker import CommentsWorker
from comments_sentiment_worker import CommentsSentimentWorker
from comments_sentiment_max import CommentsSentimentMax
from posts_worker import PostsWorker
from posts_collector import PostsCollector
from source import Source

NodeFactory = {
    "source": Source,
    "posts_worker": PostsWorker,
    "posts_collector": PostsCollector,
    "comments_worker": CommentsWorker,
    "comments_sentiment_worker": CommentsSentimentWorker,
    "comments_sentiment_max": CommentsSentimentMax,
}
