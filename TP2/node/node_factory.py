from comments_worker import CommentsWorker
from sentiment_averager import SentimentAverager
from image_streamer import ImageStreamer
from joiner import Joiner
from score_averager import ScoreAverager
from filterer import Filterer
from posts_worker import PostsWorker
from source import Source
from student_decider import StudentDecider

NodeFactory = {
    "source": Source,
    "joiner": Joiner,
    "image_streamer": ImageStreamer,
    "posts_worker": PostsWorker,
    "score_averager": ScoreAverager,
    "sentiment_averager": SentimentAverager,
    "filterer": Filterer,
    "comments_worker": CommentsWorker,
    "student_decider": StudentDecider,
}
