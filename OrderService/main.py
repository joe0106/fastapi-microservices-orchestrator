from fastapi import FastAPI
from fastapi.responses import JSONResponse
from http import HTTPStatus
from database import UserCrud
from schemas import OrderCreate

app = FastAPI()
uc = UserCrud()

@app.get("/order/{user}")
async def get_order(user: str):
    #todo check header
    if uc.get_user(user):
        return JSONResponse(
            content=uc.get_user_order_items(user),
            status_code=HTTPStatus.OK
        )
    else:
        return JSONResponse(
            content={"message": "user not found"},
            status_code=HTTPStatus.NOT_FOUND
        )

@app.post("/order/{user}")
async def new_order(user: str, new_order: OrderCreate):
    if user != new_order.user:
        return JSONResponse(
            content={"message": "not authorized"},
            status_code=HTTPStatus.BAD_REQUEST
        )
    
    if uc.get_user(user):
        result = uc.add_order(user, new_order)
        return JSONResponse(
            content=result,
            status_code=HTTPStatus.CREATED
        )
    else:
        return JSONResponse(
            content={"message": "order not created"},
            status_code=HTTPStatus.BAD_REQUEST
        )