from app.main import parse_json

# Di dalam class OrderController:

async def get_order(self, order_id: str):
    order = await self.orders_collection.find_one({"orderId": order_id})
    return parse_json(order)

async def get_all_orders(self):
    cursor = self.orders_collection.find({})
    orders = await cursor.to_list(length=100)
    return parse_json(orders)