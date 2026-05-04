from pydantic import BaseModel

class OrderBase(BaseModel):
    user: str

class OrderCreate(OrderBase):
    #order_id: str
    items: list[str]

class OrderCreateResponse(OrderBase):
    order_id: str
    items: list[str]