from fastapi import FastAPI
from fastapi.responses import JSONResponse
from http import HTTPStatus
from database import ItemCrud
from typing import Optional
from mq_consumer import Aio_Pika_Client
from contextlib import asynccontextmanager
import threading

ic = ItemCrud()
aio_pika_client = Aio_Pika_Client(ItemCrud=ic)

@asynccontextmanager
async def lifespan(app: FastAPI):
    aio_pika_thread = threading.Thread(target=aio_pika_client.run, daemon=True)
    aio_pika_thread.start()
    yield
    aio_pika_client.stop


app = FastAPI(lifespan=lifespan)


@app.get("/items/{item_id}")
@app.get("/items")
async def get_items(item_id: Optional[str] = None):
    try:
        result = ic.get_item_remain(item_id)
        return JSONResponse(
            content=result,
            status_code=HTTPStatus.OK
        )
    except Exception as e:
        return JSONResponse(
            content= {"exception": str(e)},
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR
        )