from fastapi import FastAPI
from fastapi.responses import JSONResponse
from http import HTTPStatus
from InventoryService.database import ItemCrud
from typing import Optional
from InventoryService.mq_consumer import InventoryConsumer
from contextlib import asynccontextmanager
import os
import asyncio

ic = ItemCrud()
# Allow overriding RabbitMQ URL via environment variable
AMQP_URL = os.getenv("AMQP_URL", "amqp://root:1234@127.0.0.1/")
consumer = InventoryConsumer(ic, AMQP_URL)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Start the background consumer
    task = asyncio.create_task(consumer.start())
    yield
    # Clean up
    await consumer.stop()
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass

app = FastAPI(lifespan=lifespan)

@app.get("/items/{item_id}")
@app.get("/items")
async def get_items(item_id: Optional[str] = None):
    try:
        result = ic.get_item_remain(item_id)
        if result is None:
             return JSONResponse(
                content={"message": "item not found"},
                status_code=HTTPStatus.NOT_FOUND
            )
        return JSONResponse(
            content=result,
            status_code=HTTPStatus.OK
        )
    except Exception as e:
        return JSONResponse(
            content= {"exception": str(e)},
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR
        )
