from datetime import datetime
import uuid
from app.utils import parse_json

class OrderController:
    def __init__(self, db):
        self.db = db
        self.orders_collection = db.orders
        self.menus_collection = db.menus

    async def create_order(self, customer_name: str, table_number: int):
        order = {
            "orderId": str(uuid.uuid4())[:8],
            "customerName": customer_name,
            "tableNumber": table_number,
            "status": "pending",  # ← ganti dari "draft" ke "pending"
            "items": [],
            "totalPrice": 0,
            "createdAt": datetime.now().isoformat()
        }
        result = await self.orders_collection.insert_one(order)
        order["_id"] = str(result.inserted_id)
        return order

    async def add_item(self, order_id: str, menu_id: str, quantity: int, menu_repo):
        order = await self.orders_collection.find_one({"orderId": order_id})
        if not order:
            return None

        menu = await menu_repo.find_by_menu_id(menu_id)
        if not menu:
            return None

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

        await self.orders_collection.update_one(
            {"orderId": order_id},
            {"$push": {"items": item}}
        )

        order = await self.orders_collection.find_one({"orderId": order_id})
        total = sum(i["subtotal"] for i in order.get("items", []))
        await self.orders_collection.update_one(
            {"orderId": order_id},
            {"$set": {"totalPrice": total}}
        )

        return await self.get_order(order_id)

    async def get_order(self, order_id: str):
        order = await self.orders_collection.find_one({"orderId": order_id})
        return parse_json(order)

    async def get_all_orders(self):
        cursor = self.orders_collection.find({})
        orders = await cursor.to_list(length=100)
        return parse_json(orders)

    async def confirm_order(self, order_id: str):
        """Kasir konfirmasi order → status 'paid'"""
        order = await self.orders_collection.find_one({"orderId": order_id})
        if not order:
            return None

        # Cek status harus pending
        if order["status"] != "pending":
            raise ValueError(f"Order already {order['status']}")

        # Kurangi stok bahan
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

        # Update status ke PAID
        await self.orders_collection.update_one(
            {"orderId": order_id},
            {"$set": {"status": "paid", "confirmedAt": datetime.now().isoformat()}}
        )

        return await self.get_order(order_id)

    async def update_status(self, order_id: str, status: str):
        """Update status order ke status apapun"""
        valid_status = ["pending", "paid", "cooking", "completed"]
        if status not in valid_status:
            raise ValueError(f"Invalid status. Must be one of: {valid_status}")
        
        await self.orders_collection.update_one(
            {"orderId": order_id},
            {"$set": {"status": status, "updatedAt": datetime.now().isoformat()}}
        )
        return await self.get_order(order_id)