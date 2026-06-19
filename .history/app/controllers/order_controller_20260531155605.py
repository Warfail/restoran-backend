from datetime import datetime
import uuid

class OrderController:
    def __init__(self, db):
        self.db = db
        self.orders_collection = db.get("orders", [])

    async def create_order(self, customer_name: str, table_number: int):
        order = {
            "orderId": str(uuid.uuid4())[:8],
            "customerName": customer_name,
            "tableNumber": table_number,
            "status": "draft",  # draft, confirmed, paid, cooking, done
            "items": [],
            "totalPrice": 0,
            "createdAt": datetime.now().isoformat()
        }
        self.orders_collection.append(order)
        self.db["orders"] = self.orders_collection
        return order

    async def add_item(self, order_id: str, menu_id: str, quantity: int, menu_repo):
        # Cari order
        order = None
        for o in self.orders_collection:
            if o["orderId"] == order_id:
                order = o
                break

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

        order["items"].append(item)
        order["totalPrice"] = sum(i["subtotal"] for i in order["items"])

        return order

    async def get_order(self, order_id: str):
        for o in self.orders_collection:
            if o["orderId"] == order_id:
                return o
        return None

    async def get_all_orders(self):
        return self.orders_collection

    async def confirm_order(self, order_id: str):
        """Cashier konfirmasi order -> stok berkurang"""
        order = await self.get_order(order_id)
        if not order:
            return None

        if order["status"] != "draft":
            raise ValueError(f"Order already {order['status']}")

        # Kurangi stok untuk setiap item
        for item in order["items"]:
            for menu in self.db.get("menus", []):
                if menu["menuId"] == item["menuId"]:
                    if menu["stock"] < item["quantity"]:
                        raise ValueError(f"Stok {menu['name']} tidak cukup")
                    menu["stock"] -= item["quantity"]
                    break

        order["status"] = "confirmed"
        return order

    async def update_status(self, order_id: str, status: str):
        order = await self.get_order(order_id)
        if order:
            order["status"] = status
            return order
        return None