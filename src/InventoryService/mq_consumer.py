import json

import aio_pika

from database import ItemCrud


class InventoryConsumer:
    def __init__(self, crud: ItemCrud, amqp_url: str = 'amqp://root:1234@127.0.0.1/'):
        self.crud = crud
        self.amqp_url = amqp_url
        self.connection = None
        self.exchange = None
        self.channel = None
        self.queue = None

    async def connect(self):
        print(f'Connecting to RabbitMQ at {self.amqp_url}')
        self.connection = await aio_pika.connect_robust(self.amqp_url)
        self.channel = await self.connection.channel()
        # Set QoS to process one message at a time
        await self.channel.set_qos(prefetch_count=1)
        self.exchange = await self.channel.declare_exchange(name='orders', type='fanout')
        self.queue = await self.channel.declare_queue('new-order', durable=True)
        # bind exchange to channel
        await self.queue.bind(self.exchange)

        print("Connected to RabbitMQ and queue 'new-order' declared.")

    async def process_message(self, message: aio_pika.IncomingMessage):
        async with message.process():
            try:
                body = message.body.decode()
                data = json.loads(body)
                print(f' [x] Received message: {data}')

                # The producer sends: { user_id: [ { order_id: [items] } ] }
                # We need to extract all items from this structure
                all_items = []
                for user_key in data:
                    user_data = data[user_key]
                    if isinstance(user_data, list):
                        for order_entry in user_data:
                            if isinstance(order_entry, dict):
                                for order_id in order_entry:
                                    items = order_entry[order_id]
                                    if isinstance(items, list):
                                        all_items.extend(items)

                if all_items:
                    print(f'Extract items to decrement: {all_items}')
                    self.crud.decrement_stock(all_items)
                else:
                    # Fallback for flat format if we ever change it
                    items = data.get('items', [])
                    if items:
                        self.crud.decrement_stock(items)

            except Exception as e:
                print(f'Error processing message: {e}')

    async def consume(self):
        if not self.queue:
            await self.connect()

        print(' [*] Waiting for messages. To exit press CTRL+C')
        await self.queue.consume(self.process_message)

    async def stop(self):
        if self.connection:
            await self.connection.close()
            print('RabbitMQ connection closed.')

    async def start(self):
        try:
            await self.connect()
            await self.consume()
        except Exception as e:
            print(f'Failed to start RabbitMQ consumer: {e}')
            # In a real app, you might want to retry here
