from kafka import KafkaConsumer
import time
import redis

pool = redis.ConnectionPool(host='localhost', port=6379, db=0)
consumer = KafkaConsumer('task_queue')
redis = redis.Redis(connection_pool=pool)

for msg in consumer:
    print (msg)
    redis.set('task', 'accepted')
    time.sleep(10)
    redis.set('task', 'done')