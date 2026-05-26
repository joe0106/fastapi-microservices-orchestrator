import pika
import json
import os
from schemas import OrderCreateResponse

rmqhost = os.getenv("rmqhost", "127.0.0.1")

credentials = pika.PlainCredentials('root', '1234')
parameters = pika.ConnectionParameters(
    host=rmqhost,
    port='5672',
    credentials=credentials
)
connection = pika.BlockingConnection(parameters)
channel = connection.channel()

queue_names = ['new-order', 'init-ship']

for queue in queue_names:
    channel.exchange_declare(exchange="orders", exchange_type="fanout")
    channel.queue_declare(queue=queue, durable=True)

def new_order_queue_publish(obj: OrderCreateResponse):
    channel.basic_publish(
        exchange='orders',
        routing_key='',
        body=json.dumps(obj)
    )