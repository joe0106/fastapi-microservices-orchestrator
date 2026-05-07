from aio_pika import connect_robust
from aio_pika.abc import (
    AbstractIncomingMessage,
    AbstractRobustChannel,
    AbstractRobustConnection
)
from database import ItemCrud
# ref: https://github.com/pika/pika/blob/main/examples/asynchronous_publisher_example.py
# ref: https://www.rabbitmq.com/tutorials/tutorial-one-python
# ref: https://itracer.medium.com/rabbitmq-publisher-and-consumer-with-fastapi-175fe87aefe1
class Aio_Pika_Client:

    def __init__(self, ItemCrud: ItemCrud):
        self._ampq_url: str = 'ampq"//root:1234@127.0.0.1:5672/'
        self._connection: AbstractRobustConnection = None
        self._channel: AbstractRobustChannel = None
        self._stopping = False
        self._ic = ItemCrud
        self._consumer_tag = None
        self._queue = None
        self._queue_name = 'new-order'
        # self.connection = pika.BlockingConnection(
        #     pika.ConnectionParameters(self.parameters)
        # )
        # self.channel = self.connection.channel()
        # self.publish_queue = self.channel.queue_declare(queue=self.publish_queue_name)
        # self.response = None
        # self.process_callable = process_callable

    async def connect(self):
        self._connection = await connect_robust(url=self._ampq_url)
        self._channel = await self._connection.channel()
        self._queue = await self._channel.declare_queue(
            name=self._queue_name,
            durable=True
        )
        await self._queue.consume(self.on_message)

    async def on_message(self, msg: AbstractIncomingMessage):
        async with msg.process():
            print("received message")

            if msg.body:
                orders = msg.body.values() #the user's order objects
                order_id = orders.values() #the order ids in the user's order objects
                for order_items in order_id: #the items in the order ids that ar in the users's order object
                    self._ic.decrement_stock(order_items)
                #手動對rabbitMQ送出ack，通知其可以準備刪掉已處理的訊息
                msg.ack(multiple=False)

                print("done processing message")
            else:
                print("no body to process message")

    async def run(self):
        self._connection = await self.connect()

    async def stop(self):
        self._stopping = True
        if self._channel is not None:
            self._channel.close()
        if self._connection is not None:
            self._connection.close()