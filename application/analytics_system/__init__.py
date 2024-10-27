from .tasks import AnalyticsQueue
import atexit


def init_analytics(app):
    queue = AnalyticsQueue.initialize(app)

    def cleanup():
        AnalyticsQueue.shutdown()

    atexit.register(cleanup)

    return queue