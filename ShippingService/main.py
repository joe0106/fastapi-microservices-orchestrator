from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from http import HTTPStatus
from typing import Optional
from ShippingService.mq_consumer import ShippingConsumer
from contextlib import asynccontextmanager
from ShippingService.database import ShippingCrud
import os
import asyncio

sc = ShippingCrud()
AMQP_URL = os.getenv("AMQP_URL", "amqp://root:1234@127.0.0.1/")
consumer = ShippingConsumer(sc, AMQP_URL)

@asynccontextmanager
async def lifespan(app: FastAPI):
    task = asyncio.create_task(consumer.start())
    yield
    await consumer.stop()
    task.cancel
    try:
        await task
    except asyncio.CancelledError:
        pass

app = FastAPI(lifespan=lifespan)

@app.get("/shipping/{order_id}")
@app.get("/shipping")
def check_shipping_status(order_id: Optional[str] = None):
    try:
        result = sc.get_shipping_status(order_id)

        if not result:
            return JSONResponse(
                content={"message": "order id not found"},
                status_code=HTTPStatus.NOT_FOUND
            )
        return JSONResponse(
            content=jsonable_encoder(result),
            status_code=HTTPStatus.OK
        )
    except Exception as e:
        return JSONResponse(
            content={"exception": str(e)},
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR
        )