import redis
from rq import Worker, Queue
from shared.config import settings

conn = redis.Redis.from_url(settings.redis_url)
q = Queue(connection=conn)

if __name__ == "__main__":
    worker = Worker([q], connection=conn)
    worker.work()
