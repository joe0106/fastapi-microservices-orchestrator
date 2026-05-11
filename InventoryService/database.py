items = {
    "item1": 3,
    "item2": 3,
    "item3": 3
}

class ItemCrud:
    def get_item_remain(self, search_item: str = None):
        if search_item:
            if search_item not in items:
                return None
            return {search_item: items[search_item]}
        else:
            return items

    def decrement_stock(self, item_list: list[str]):
        for item_id in item_list:
            if item_id in items:
                if items[item_id] > 0:
                    items[item_id] -= 1
                    print(f"Decremented stock for {item_id}. New stock: {items[item_id]}")
                else:
                    print(f"Stock for {item_id} is already 0.")
            else:
                print(f"Item {item_id} not found in inventory.")