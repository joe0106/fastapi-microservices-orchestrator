# Order Service
A FastAPI backend which uses RabbitMQ as a message broker to update product stock when order is placed

## Start Container
```bash
cd OrderService
MODE=dev uv run fastapi dev --port 8001
```
確認RabbitMQ container 是否存在
```bash
# start RabbitMQ service at port 5672
# port 15762 for web UI
docker run --rm -p 5672:5672 -p 15672:15672 -e RABBITMQ_DEFAULT_USER=root -e RABBITMQ_DEFAULT_PASS=1234 rabbitmq:management
```

## RabbitMQ producer/publisher

當OrderService接到新的訂單時，將訂單結果發送訊息至RabbitMQ作為一個message broker及message queue

1. message queue: 作為一個message queue，他在微服務中是一個buffer，暫時將訊息暫時全部存入其中，等待被非同步處理。 流量變大時，也會避免服務因為負荷瞬間變大而崩潰
2. message broker: 在架構中作為一個中間人，OrderService不需要知道InventoryService或其他下游服務是什麼，他只要將訊息交給message broker就好，有著解耦的作用。message broker也可以決定資料的流向，決定訊息會被非派到哪些頻道、服務中

### 踩到的坑
`channel.queue_declare(queue='<queue-name>')`
這樣的宣告方式會失敗，logs中寫道：「operation queue.declare caused a connection exception internal_error: "Feature `transient_nonexcl_queues` is deprecated.\nBy default, this feature is not permitted anymore.\nThe feature will be removed from a future major RabbitMQ version, regardless of the configuration; actual version to be determined.\nTo continue using this feature when it is not permitted by default, set the following parameter in your configuration:\n    \"deprecated_features.permit.transient_nonexcl_queues = true\""」
簡言之就是，因為queue_declare()寫法的預設參數durable和exclusive
durable參數(預設為False)設定這個rabbitmq是否能禁得起機器的重啟，如果希望重啟能保留資料，durable就要設定為true，而durable等於true就是non-transient。
exclusive參數(預設為False)設定為true代表queue是這個連線私有的，而斷線後將會被清除。
所以，在宣告queue時，至少要使用其中一個設定才能避免這個錯誤