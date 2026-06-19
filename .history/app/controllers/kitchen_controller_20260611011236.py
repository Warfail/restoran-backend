from app.main import parse_json

class KitchenController:
    def __init__(self, db):
        self.db = db
        self.orders_collection = db.orders

    async def get_pending_orders(self):
        """Order yang sudah dikonfirmasi tapi belum dimasak"""
        cursor = self.orders_collection.find({"status": "paid"})
        orders = await cursor.to_list(length=100)
        return parse_json(orders)

    async def get_cooking_orders(self):
        """Order yang sedang dimasak"""
        cursor = self.orders_collection.find({"status": "cooking"})
        orders = await cursor.to_list(length=100)
        return parse_json(orders)

    async def start_cooking(self, order_id: str):
        order = await self.orders_collection.find_one({"orderId": order_id})
        if not order:
            return None

        if order["status"] != "paid":
            raise ValueError(f"Cannot start cooking order with status {order['status']}")

        await self.orders_collection.update_one(
            {"orderId": order_id},
            {"$set": {"status": "cooking"}}
        )
        return await self.get_order(order_id)

    async def done_cooking(self, order_id: str):
        order = await self.orders_collection.find_one({"orderId": order_id})
        if not order:
            return None

        if order["status"] != "cooking":
            raise ValueError(f"Cannot complete order with status {order['status']}")

        await self.orders_collection.update_one(
            {"orderId": order_id},
            {"$set": {"status": "done"}}
        )
        return await self.get_order(order_id)

    async def get_order(self, order_id: str):
        order = await self.orders_collection.find_one({"orderId": order_id})
        return parse_json(order)