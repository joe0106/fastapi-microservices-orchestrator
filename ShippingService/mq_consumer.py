import aio_pika
import json
from database import ShippingCrud

class ShippingConsumer:
    def __init__(self, crud: ShippingCrud, amqp_url: str = "amqp://root:1234@127.0.0.1/"):
        self.crud = crud
        self.amqp_url = amqp_url
        self.connection = None
        self.exchange = None
        self.channel = None
        self.queue = None

    async def connect(self):
        print(f"Connecting to RabbitMQ at {self.amqp_url}")
        self.connection = await aio_pika.connect_robust(self.amqp_url)
        self.channel = await self.connection.channel()
        # Set QoS to process one message at a time
        await self.channel.set_qos(prefetch_count=1)
        self.exchange = await self.channel.declare_exchange(name="orders", type="fanout")
        self.queue = await self.channel.declare_queue("init-ship", durable=True)
        #bind exchange to channel
        await self.queue.bind(self.exchange)

        print("Connected to RabbitMQ and queue 'init-ship' declared.")

    async def process_message(self, message: aio_pika.IncomingMessage):
        async with message.process():
            try:
                body = message.body.decode()
                data = json.loads(body)
                print(f" [x] Received message: {data}")
                
                # The producer sends: { user_id: [ { order_id: [items] } ] }
                # We need to extract all items from this structure
                all_orders = []
                for user_key in data:
                    user_data = data[user_key]
                    if isinstance(user_data, list):
                        for order_entry in user_data:
                            if isinstance(order_entry, dict):
                                for order_id in order_entry:
                                    all_orders.extend(order_id)
                
                if order_entry:
                    for order_id in order_entry:
                        print(f"init order_id: {order_id} shipping status.")
                        self.crud.init_shipping_status(order_id)
                else:
                    pass
                
            except Exception as e:
                print(f"Error processing message: {e}")

    async def consume(self):
        if not self.queue:
            await self.connect()
        
        print(" [*] Waiting for messages. To exit press CTRL+C")
        await self.queue.consume(self.process_message)

    async def stop(self):
        if self.connection:
            await self.connection.close()
            print("RabbitMQ connection closed.")

    async def start(self):
        try:
            await self.connect()
            await self.consume()
        except Exception as e:
            print(f"Failed to start RabbitMQ consumer: {e}")
            # In a real app, you might want to retry here
