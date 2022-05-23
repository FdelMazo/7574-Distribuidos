from posts_worker import PostsWorker
from posts_collector import PostsCollector
from source import Source

NodeFactory = {
    "source": Source,
    "posts_worker": PostsWorker,
    "posts_collector": PostsCollector,
}
