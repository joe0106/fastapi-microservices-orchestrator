import pika
# ref: https://github.com/pika/pika/blob/main/examples/asynchronous_publisher_example.py
# ref: https://www.rabbitmq.com/tutorials/tutorial-one-python
# ref: https://itracer.medium.com/rabbitmq-publisher-and-consumer-with-fastapi-175fe87aefe1
class PikaClient:

    # credentials = pika.PlainCredentials('root', '1234')
    # parameters = pika.ConnectionParameters(
    #     host='127.0.0.1',
    #     port='5672',
    #     credentials=credentials
    # )

    def __init__(self):
        self._credentials = pika.PlainCredentials('root', '1234')
        self._parameters = pika.ConnectionParameters(
            host='127.0.0.1',
            port='5672',
            credentials=self._credentials
        )
        self._connection = None
        self._channel = None
        self._stopping = False
        # self.publish_queue_name = 'new-order'
        # self.connection = pika.BlockingConnection(
        #     pika.ConnectionParameters(self.parameters)
        # )
        # self.channel = self.connection.channel()
        # self.publish_queue = self.channel.queue_declare(queue=self.publish_queue_name)
        # self.callback_queue = self.publish_queue.method.queue
        # self.response = None
        # self.process_callable = process_callable

    def connect(self):
        #on_open_callback
        #on_open_error_callback
        #on_close_callback
        # return pika.BlockingConnection(self._parameters)
        return pika.SelectConnection(
            self._parameters,
            on_open_callback=self.on_connection_open,
            on_open_error_callback=self.on_connection_open_error,
            on_close_callback=self.on_connection_closed
        )
    
    def on_connection_open(self, _unused_connection):
        self.open_channel()

    def on_connection_open_error(self, _unused_connection, err):
        self._connection.ioloop.call_later(5, self._connection.ioloop.stop)

    def on_connection_closed(self, _unused_connection, reason):
        self._channel = None
        if self._stopping:
            self._connection.ioloop.stop()
        else:
            self._connection.ioloop.call_later(5, self._connection.ioloop.stop)

    def open_channel(self):
        #self._connection.channel()
        self._connection.channel(on_open_callback=self.on_channel_open)

    def on_channel_open(self, channel):
        self._channel = channel
        self.add_on_channel_close_callback()
        self.setup_queue('new-order')

    def add_on_channel_close_callback(self):
        self._channel.add_on_close_callback(self.on_channel_closed)

    def on_channel_closed(self, channel, reason):
        self._channel = None
        if not self._stopping:
            self._connection.close()

    def setup_queue(self, queue_name):
        self._channel.queue_declare(queue=queue_name, durable=True)
        self.consume(queue_name)

    def consume(self, queue_name):
        self._channel.basic_consume(queue_name, self.handle_delivery)

    def handle_delivery(self, channel, method, header, body):
        print(body)

    def stop(self):
        self._stopping = True
        self.close_channel()
        self.close_connection()
    
    def close_channel(self):
        if self._channel is not None:
            self._channel.close()
    
    def close_connection(self):
        if self._connection is not None:
            self._connection.close()

    def run(self):
        while not self._stopping:
            self._connection = None

            try:
                self._connection = self.connect()
                self._connection.ioloop.start()
            except KeyboardInterrupt:
                self.stop()
                if (self._connection is None and not self._connection.is_closed):
                    self._connection.ioloop.start()