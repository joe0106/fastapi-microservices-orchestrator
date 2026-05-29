from contextlib import asynccontextmanager
from http import HTTPStatus

from fastapi import FastAPI
from fastapi.responses import JSONResponse

from database import UserCrud
from mq_producer import new_order_queue_publish
from schemas import OrderCreate, OrderCreateResponse


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    # if connection.is_open:
    #     connection.close()
    #     print('RabbitMQ connection closed')


app = FastAPI(lifespan=lifespan)

uc = UserCrud()


@app.get('/order/{user}')
async def get_order(user: str):
    # todo check header
    if uc.get_user(user):
        return JSONResponse(content=uc.get_user_order_items(user), status_code=HTTPStatus.OK)
    else:
        return JSONResponse(content={'message': 'user not found'}, status_code=HTTPStatus.NOT_FOUND)


@app.post('/order/{user}', response_model=OrderCreateResponse)
async def new_order(user: str, new_order: OrderCreate):
    try:
        if user != new_order.user:
            return JSONResponse(
                content={'message': 'not authorized'},
                status_code=HTTPStatus.BAD_REQUEST,
            )

        if uc.get_user(user):
            result = uc.add_order(user, new_order)

            new_order_queue_publish(result)

            return JSONResponse(content=result, status_code=HTTPStatus.CREATED)
        else:
            return JSONResponse(
                content={'message': 'order not created'},
                status_code=HTTPStatus.BAD_REQUEST,
            )

    except Exception as e:
        return JSONResponse(
            content={'exception': str(e)}, status_code=HTTPStatus.INTERNAL_SERVER_ERROR
        )
