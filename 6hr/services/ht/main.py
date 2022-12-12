from http.server import BaseHTTPRequestHandler, HTTPServer
from kafka import KafkaProducer
import redis
import time
import signal

producer = KafkaProducer(bootstrap_servers='localhost:9092')
pool = redis.ConnectionPool(host='localhost', port=6379, db=0)
redis = redis.Redis(connection_pool=pool)

class HttpProcessor(BaseHTTPRequestHandler):
    def __init__(self):
        self.state = 'open'
        self.counter = 0
        self.limit_from_open = 2
        self.limit_from_closed = 2
        self.limit_from_half_open = 2
        self.timeout_from_closed = 5
        signal.signal(signal.SIGTERM, self.cleanup)
        self.producer = KafkaProducer(bootstrap_servers='localhost:9092')
        self.pool = redis.ConnectionPool(host='localhost', port=6379, db=0)

    def cleanup(self):
        self.producer.close()

    def connectredis_with_cb(self):
        if self.state == 'open':
            self.counter = 0
            while self.counter < self.limit_from_open:
                try:
                    redis = redis.Redis(connection_pool=self.pool)
                    return redis
                except:
                    self.counter += 1
            self.state = 'closed'
            self.counter = 0

        if self.state == 'half_open':
            try:
                redis = redis.Redis(connection_pool=self.pool)
                self.counter += 1
                if self.counter == self.limit_from_half_open:
                    self.state = 'open'
                return redis
            except:
                self.state = 'closed'

        if self.state == 'closed':
            self.counter = 0
            while True:
                time.sleep(self.timeout_from_closed)
                try:
                    redis = redis.Redis(connection_pool=self.pool)
                    self.state = 'half_open'
                    self.counter = 0
                    return redis
                except:
                    self.counter += 1

    def do_GET(self):
        request = self.requestline
        # print(request)
        if request.startswith('/task'):
            redis = self.connectredis_with_cb()
            redis.set('task' + request, 'in_queue')
            self.producer.send('task_queue', b'task_no')
            self.send_response(200)
            self.send_header('content-type','text/html')
            self.end_headers()
            self.wfile.write(b"hi!")
        if request.startswith('/healthcheck'):
            self.send_response(200)
            self.send_header('content-type','text/html')
            self.end_headers()
            try:
                self.log_message('Healthcheck: ok!')
                KafkaProducer(bootstrap_servers='localhost:9092')
                self.wfile.write(b"ok")
            except:
                self.log_error('Healthcheck: Not ok!')
                self.wfile.write(b"not ok")

def main():
    serv = HTTPServer(("localhost",8901), HttpProcessor)
    serv.serve_forever()

if __name__ == '__main__':
    main()
