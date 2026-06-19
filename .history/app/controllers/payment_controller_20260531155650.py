import uuid
from datetime import datetime

class PaymentController:
    def __init__(self, db):
        self.db = db
        self.payments_collection = db.get("payments", [])

    async def process_payment(self, order_id: str, amount_paid: float):
        # Cari order
        order = None
        orders = self.db.get("orders", [])
        for o in orders:
            if o["orderId"] == order_id:
                order = o
                break

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

        self.payments_collection.append(payment)
        self.db["payments"] = self.payments_collection

        # Update status order
        order["status"] = "paid"

        return {"success": True, "payment": payment, "change": change}

    async def get_receipt(self, order_id: str):
        # Cari payment berdasarkan order_id
        for payment in self.payments_collection:
            if payment["orderId"] == order_id:
                # Cari order
                order = None
                for o in self.db.get("orders", []):
                    if o["orderId"] == order_id:
                        order = o
                        break
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
        return None