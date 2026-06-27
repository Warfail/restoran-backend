from app.utils import parse_json
from datetime import datetime
from serializers import serialize_document, serialize_list, serialize_value

class KitchenController:
    def __init__(self, db):
        self.db = db
        self.orders_collection = db.orders

    async def get_pending_orders(self):
        """Order yang sudah dibayar tapi belum dimasak (status: paid)"""
        cursor = self.orders_collection.find({"status": "paid"})
        orders = await cursor.to_list(length=100)
        return serialize_list(orders)

    async def get_cooking_orders(self):
        """Order yang sedang dimasak (status: cooking)"""
        cursor = self.orders_collection.find({"status": "cooking"})
        orders = await cursor.to_list(length=100)
        return serialize_list(orders)

    async def get_all_kitchen_orders(self):
        """Ambil semua order untuk kitchen (paid + cooking)"""
        cursor = self.orders_collection.find({
            "status": {"$in": ["paid", "cooking"]}
        })
        orders = await cursor.to_list(length=100)
        return serialize_list(orders)

    async def start_cooking(self, order_id: str):
        """Kitchen mulai masak → status 'cooking'"""
        order = await self.orders_collection.find_one({"orderId": order_id})
        if not order:
            return None

        if order["status"] != "paid":
            raise ValueError(f"Cannot start cooking order with status {order['status']}. Must be 'paid'")

        # Deduct inventory stock based on recipe (BoM)
        if not order.get("ingredientsDeducted", False):
            for item in order.get("items", []):
                menu_id_val = item.get("menuId")
                menu = await self.db.menus.find_one({
                    "$or": [{"menuId": menu_id_val}, {"kode": menu_id_val}]
                })
                if menu and menu.get("ingredients"):
                    for ing in menu["ingredients"]:
                        inv_id = ing.get("inventory_id")
                        qty_needed = ing.get("quantity_needed", 0) * item.get("quantity", 1)
                        if inv_id and qty_needed > 0:
                            from bson import ObjectId
                            try:
                                await self.db.inventory.update_one(
                                    {"_id": ObjectId(inv_id)},
                                    {"$inc": {"stock": -qty_needed}}
                                )
                            except Exception as e:
                                print(f"Error deducting stock: {e}")

            # Mark as deducted to avoid double counting
            await self.orders_collection.update_one(
                {"orderId": order_id},
                {"$set": {"ingredientsDeducted": True}}
            )

        await self.orders_collection.update_one(
            {"orderId": order_id},
            {"$set": {"status": "cooking", "startedAt": datetime.now().isoformat()}}
        )
        return await self.get_order(order_id)

    async def done_cooking(self, order_id: str):
        """Kitchen selesai masak → status 'completed'"""
        order = await self.orders_collection.find_one({"orderId": order_id})
        if not order:
            return None

        if order["status"] != "cooking":
            raise ValueError(f"Cannot complete order with status {order['status']}. Must be 'cooking'")

        await self.orders_collection.update_one(
            {"orderId": order_id},
            {"$set": {"status": "completed", "completedAt": datetime.now().isoformat()}}
        )
        return await self.get_order(order_id)

    async def get_order(self, order_id: str):
        order = await self.orders_collection.find_one({"orderId": order_id})
        return serialize_document(order)