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