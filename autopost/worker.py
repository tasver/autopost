import os
from rq import Worker, Queue, Connection
from datetime import datetime,timedelta
from redis import Redis
from rq.registry import ScheduledJobRegistry
from autopost.settings import REDISTOGO_URL

redis = Redis()

redis_url = os.getenv(REDISTOGO_URL, 'redis://localhost:5000')
redis = redis.from_url(redis_url)

queue = Queue(connection=redis)
worker = Worker(queues=[queue], connection=redis)
worker.work(with_scheduler=True)


# Schedules job to be run at 9:15, October 10th in the local timezone

  # Outputs True as job is placed in ScheduledJobRegistry


#listen = ['high', 'default', 'low']

#redis_url = os.getenv('REDISTOGO_URL', 'redis://localhost:6379')

#queue = Queue(name='default', connection=Redis())

# Schedules job to be run at 9:15, October 10th in the local timezone
#job = queue.enqueue_at(datetime(2019, 10, 8, 9, 15), say_hello)


#conn = redis.from_url(redis_url)

#if __name__ == '__main__':
#    with Connection(conn):
##        worker = Worker(map(Queue, listen))
#       worker.work()
