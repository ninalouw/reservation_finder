import os
import pickle
import redis
from rq import Worker, Queue, Connection
pickle.HIGHEST_PROTOCOL = 2

listen = ['high', 'default', 'low']

redis_url = os.getenv('REDISTOGO_URL', 'redis://localhost:6379')

conn = redis.from_url(redis_url)

if __name__ == '__main__':
    with Connection(conn):
        registry = Queue.failed_job_registry
        worker = Worker(map(Queue, listen))
        worker.work()
