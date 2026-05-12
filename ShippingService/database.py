from enum import Enum

class Status(str, Enum):
    order_recieved = "order_recieved"
    in_transit = "in_transit"

shipping_status = {
    "order-id-a": "order_recieved",
    "order-id-b1": "order_recieved",
    "order-id-b2": "order_recieved",
    "order-id-c": "order_recieved"
    }

class ShippingCrud:

    def get_shipping_status(self, order: str):
        if order:
            if order not in shipping_status:
                return None
            return shipping_status.get(order)
        else:
            return shipping_status
        
    def init_shipping_status(self, order: str):
        shipping_status[order] = Status.order_recieved.value

    def order_payed(self, order: str):
        shipping_status[order] = Status.in_transit.value