# Inventory Service
A FastAPI backend utilizing asyncio tasks as a background service, which listens for RabbitMQ messages to process

## Start Container
```bash
cd InventoryService
MODE=dev uv run fastapi dev --port 8002
```

## RabbitMQConsumer
處理RabbitMQ訊息的服務，這個message consumer會在fastapi的背景下執行，下列是重要的RabbitMQ設定

### connect()
1. aio_pika.robust_connection(): 宣告對rabbitmq的連線，而對rabbitMQ服務來說publisher, consumer使用pika和aio_pika是不衝突的，只要連線設定正常即可
robust_connection()會比connection()來得更完善，它將網路中斷或連線失敗的處理設計的更優雅
2. connection.channel(): 建立一個訊息佇列的頻道供publisher, consumer使用
3. channel.set_qos(prefetch_count=1): 設定prefetch_count，代表一次要取幾個訊息
4. channel.declare_queue(): 宣告queue，宣告publisher佇列訊息的頻道名稱讓consumer取用

### process_message()
將佇列中的訊息取出後處理，例如異動庫存
- async with message.process(self, message: aio_pika.IncomingMessage): 帶入預設的參數將訊息從`message.body`中取出

> 需要ack嗎？
如果需要確保消息被完全處理、不丟失

### stop()
connection關閉，供fastapi生命週期結束時呼叫

### start()
consumer task的啟動點，呼叫connect(), consume()

## main.py
背景工作task要隨著fastapi的生命週期起始和結束
- 使用`@asynccontextmanager`宣告fastapi的lifespan
- 使用`asyncio.createtask(consumer.start())`啟動consumer
- `yield`進入fastapi的生命週期
- 結束時，也要做consumer.stop(), task.cancel()
- await task 等待task真正結束、釋放資源
- except asyncio.CancelledError 等等測試
- 初始化FastAPI帶入lifespan