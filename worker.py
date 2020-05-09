"""import os
from rq import Worker, Queue, Connection
from datetime import datetime,timedelta
from redis import Redis
from rq.registry import ScheduledJobRegistry
from autopost.settings import REDISTOGO_URL
import urlparse

redis = Redis()

redis_url = os.getenv('REDISTOGO_URL')

urlparse.uses_netloc.append('redis')
url = urlparse.urlparse(redis_url)
conn = Redis(host=url.hostname, port=url.port, db=0, password=url.password)

#redis_url = os.getenv(REDISTOGO_URL)
redis = redis.from_url(REDISTOGO_URL)
#urlparse.uses_netloc.append('redis')
#url = urlparse.urlparse(redis_url)
#conn = Redis(host=url.hostname, port=url.port, db=0, password=url.password)
queue = Queue(connection=redis)
worker = Worker(queues=[queue], connection=redis)
worker.work(with_scheduler=True)
"""
import os
import redis
from rq import Worker, Queue, Connection

listen = ['high', 'default', 'low']
redis_url = os.getenv('REDISTOGO_URL', 'redis://localhost:6379')
conn = redis.from_url(redis_url)
if __name__ == '__main__':
    with Connection(conn):
        worker = Worker(map(Queue, listen))
        worker.work()



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
