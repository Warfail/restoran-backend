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
            "status": "draft",
            "items": [],
            "totalPrice": 0,
            "createdAt": datetime.now().isoformat()
        }
        self.orders_collection.append(order)
        # Simpan ke mock_db.json
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
    
    async def update_status(self, order_id: str, status: str):
        order = await self.get_order(order_id)
        if order:
            order["status"] = status
            return order
        return None