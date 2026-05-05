import pika
import json
from schemas import OrderCreateResponse

credentials = pika.PlainCredentials('root', '1234')
parameters = pika.ConnectionParameters(
    host='127.0.0.1',
    port='5672',
    credentials=credentials
)
connection = pika.BlockingConnection(parameters)
channel = connection.channel()

channel.queue_declare(queue='new-order', durable=True)

def new_order_queue_publish(obj: OrderCreateResponse):
    channel.basic_publish(
        exchange='',
        routing_key='new-order',
        body=json.dumps(obj)
    )