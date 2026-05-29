from schemas import OrderCreate

users = ['user-a', 'user-b', 'user-c']

user_orders = {
    'user-a': ['order-id-a'],
    'user-b': ['order-id-b1', 'order-id-b2'],
    'user-c': ['order-id-c'],
}

order_items = {
    'order-id-a': ['item1', 'item2'],
    'order-id-b1': ['item1', 'item2'],
    'order-id-b2': ['item2', 'item3'],
    'order-id-c': ['item2'],
}


class UserCrud:
    def get_user(self, user: str):
        return user in users

    def get_user_order_items(self, user: str):
        return {
            user: [
                {order_id: order_items.get(order_id, [])} for order_id in user_orders.get(user, [])
            ]
        }

    def add_order(self, user: str, new_order: OrderCreate):
        new_order_id = f'order-id-{new_order.user}-auto'
        user_orders[user].append(new_order_id)

        temp_list = []
        for item in new_order.items:
            temp_list.append(item)

        order_items[new_order_id] = temp_list

        return {user: [{new_order_id: order_items[new_order_id]}]}
