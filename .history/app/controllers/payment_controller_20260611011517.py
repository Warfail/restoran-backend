import uuid
from datetime import datetime
from app.utils import parse_json

class PaymentController:
    def __init__(self, db):
        self.db = db
        self.orders_collection = db.orders
        self.payments_collection = db.payments

    async def process_payment(self, order_id: str, amount_paid: float):
        order = await self.orders_collection.find_one({"orderId": order_id})
        if not order:
            return None

        if order["status"] != "confirmed":
            return {"success": False, "message": "Order belum dikonfirmasi kasir"}

        total = order["totalPrice"]

        if amount_paid < total:
            return {"success": False, "message": f"Uang kurang. Total: Rp{total}"}

        change = amount_paid - total

        payment = {
            "paymentId": str(uuid.uuid4())[:8],
            "orderId": order_id,
            "amountPaid": amount_paid,
            "totalPrice": total,
            "change": change,
            "status": "success",
            "paymentDate": datetime.now().isoformat()
        }

        await self.payments_collection.insert_one(payment)

        # Update status order
        await self.orders_collection.update_one(
            {"orderId": order_id},
            {"$set": {"status": "paid"}}
        )

        return {"success": True, "payment": parse_json(payment), "change": change}

    async def get_receipt(self, order_id: str):
        payment = await self.payments_collection.find_one({"orderId": order_id})
        if not payment:
            return None

        order = await self.orders_collection.find_one({"orderId": order_id})
        
        return {
            "receiptId": payment["paymentId"],
            "orderId": order_id,
            "customerName": order.get("customerName") if order else "-",
            "tableNumber": order.get("tableNumber") if order else "-",
            "items": order.get("items", []) if order else [],
            "totalPrice": payment["totalPrice"],
            "amountPaid": payment["amountPaid"],
            "change": payment["change"],
            "paymentDate": payment["paymentDate"]
        }