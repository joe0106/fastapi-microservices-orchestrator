from fastapi import FastAPI
from fastapi.responses import JSONResponse
from http import HTTPStatus
from database import ItemCrud
from typing import Optional
from mq_consumer import PikaClient

app = FastAPI()
ic = ItemCrud()
pika_client = PikaClient()
#pika_client.run()

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