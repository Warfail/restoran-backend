class KitchenController:
    def __init__(self, db):
        self.db = db
        self.orders_collection = db.get("orders", [])

    async def get_pending_orders(self):
        """Order yang sudah dikonfirmasi tapi belum dimasak"""
        return [o for o in self.orders_collection if o.get("status") == "paid"]

    async def get_cooking_orders(self):
        """Order yang sedang dimasak"""
        return [o for o in self.orders_collection if o.get("status") == "cooking"]

    async def start_cooking(self, order_id: str):
        order = None
        for o in self.orders_collection:
            if o["orderId"] == order_id:
                order = o
                break

        if not order:
            return None

        if order["status"] != "paid":
            raise ValueError(f"Cannot start cooking order with status {order['status']}")

        order["status"] = "cooking"
        return order

    async def done_cooking(self, order_id: str):
        order = None
        for o in self.orders_collection:
            if o["orderId"] == order_id:
                order = o
                break

        if not order:
            return None

        if order["status"] != "cooking":
            raise ValueError(f"Cannot complete order with status {order['status']}")

        order["status"] = "done"
        return order