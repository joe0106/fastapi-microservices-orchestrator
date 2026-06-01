import json
import os

import pika

from schemas import OrderCreateResponse


def new_order_queue_publish(obj: OrderCreateResponse):

    rmqhost = os.getenv('rmqhost', '127.0.0.1')
    credentials = pika.PlainCredentials('root', '1234')
    parameters = pika.ConnectionParameters(host=rmqhost, port='5672', credentials=credentials)

    # connection = pika.BlockingConnection(parameters)
    connection = None

    try:
        with pika.BlockingConnection(parameters) as connection:
            channel = connection.channel()
            channel.exchange_declare(exchange='orders', exchange_type='fanout')

            queue_names = ['new-order', 'init-ship']
            for queue in queue_names:
                channel.queue_declare(queue=queue, durable=True)

            channel.basic_publish(exchange='orders', routing_key='', body=json.dumps(obj))
    except Exception as e:
        print(f'rabbitmq producer發生錯誤: {str(e)}')
