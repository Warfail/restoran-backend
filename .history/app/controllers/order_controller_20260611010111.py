from datetime import datetime
import uuid
from bson import ObjectId
from bson import json_util
import json


class OrderController:
    def __init__(self, db):
        self.db = db
        self.orders_collection = db.orders  # MongoDB collection
        self.menus_collection = db.menus    # MongoDB collection

    async def create_order(self, customer_name: str, table_number: int):
        order = {
            "orderId": str(uuid.uuid4())[:8],
            "customerName": customer_name,
            "tableNumber": table_number,
            "status": "draft",
            "items": [],
            "totalPrice": 0,
            "createdAt": datetime.now().isoformat()
        }
        result = await self.orders_collection.insert_one(order)
        order["_id"] = str(result.inserted_id)
        return order

    async def add_item(self, order_id: str, menu_id: str, quantity: int, menu_repo):
        # Cari order
        order = await self.orders_collection.find_one({"orderId": order_id})
        if not order:
            return None

        # Cari menu
        menu = await menu_repo.find_by_menu_id(menu_id)
        if not menu:
            return None

        # Cek stok
        if menu["stock"] < quantity:
            raise ValueError(f"Stok {menu['name']} tidak cukup. Sisa: {menu['stock']}")

        subtotal = menu["price"] * quantity

        item = {
            "menuId": menu_id,
            "name": menu["name"],
            "price": menu["price"],
            "quantity": quantity,
            "subtotal": subtotal
        }

        # Update order dengan push item
        await self.orders_collection.update_one(
            {"orderId": order_id},
            {"$push": {"items": item}}
        )

        # Update total price
        order = await self.orders_collection.find_one({"orderId": order_id})
        total = sum(i["subtotal"] for i in order.get("items", []))
        await self.orders_collection.update_one(
            {"orderId": order_id},
            {"$set": {"totalPrice": total}}
        )

        return await self.orders_collection.find_one({"orderId": order_id})

    async def get_order(self, order_id: str):
        order = await self.orders_collection.find_one({"orderId": order_id})
        if order and "_id" in order:
            order["_id"] = str(order["_id"])
        return order

    async def get_all_orders(self):
        cursor = self.orders_collection.find({})
        orders = await cursor.to_list(length=100)
        for order in orders:
            order["_id"] = str(order["_id"])
        return orders

    async def confirm_order(self, order_id: str):
        """Cashier konfirmasi order -> stok berkurang"""
        order = await self.orders_collection.find_one({"orderId": order_id})
        if not order:
            return None

        if order["status"] != "draft":
            raise ValueError(f"Order already {order['status']}")

        # Kurangi stok untuk setiap item
        for item in order.get("items", []):
            menu = await self.menus_collection.find_one({"menuId": item["menuId"]})
            if menu:
                if menu["stock"] < item["quantity"]:
                    raise ValueError(f"Stok {menu['name']} tidak cukup")
                new_stock = menu["stock"] - item["quantity"]
                await self.menus_collection.update_one(
                    {"menuId": item["menuId"]},
                    {"$set": {"stock": new_stock}}
                )

        # Update status order
        await self.orders_collection.update_one(
            {"orderId": order_id},
            {"$set": {"status": "confirmed"}}
        )

        return await self.get_order(order_id)

    async def update_status(self, order_id: str, status: str):
        await self.orders_collection.update_one(
            {"orderId": order_id},
            {"$set": {"status": status}}
        )
        return await self.get_order(order_id)
    
    async def get_order(self, order_id: str):
        order = await self.orders_collection.find_one({"orderId": order_id})
        return json.loads(json_util.dumps(order))

    async def get_all_orders(self):
        cursor = self.orders_collection.find({})
        orders = await cursor.to_list(length=100)
        return json.loads(json_util.dumps(orders))