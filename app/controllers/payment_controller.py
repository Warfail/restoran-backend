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

        if order["status"] not in ["pending", "confirmed"]:
            return {"success": False, "message": "Order sudah dibayar atau tidak valid"}

        total = order.get("totalAmount", order.get("totalPrice", 0))

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

        # Update status order and deduct stock
        from app.controllers.order_controller import OrderController
        order_ctrl = OrderController(self.db)
        await order_ctrl.update_status(order_id, "paid")

        return {"success": True, "payment": parse_json(payment), "change": change}

    async def get_receipt(self, order_id: str):
        payment = await self.payments_collection.find_one({"orderId": order_id})
        order = await self.orders_collection.find_one({"orderId": order_id})
        
        if not order:
            return None

        # Jika pembayaran dilakukan online (QRIS/Transfer), record di collection payments mungkin tidak ada.
        # Kita fallback menggunakan data dari collection orders.
        if not payment:
            total = order.get("totalAmount", order.get("totalPrice", 0))
            return {
                "receiptId": f"REC-{order_id[-6:]}",
                "orderId": order_id,
                "customerName": order.get("customerName", "-"),
                "tableNumber": order.get("tableNumber", "-"),
                "items": order.get("items", []),
                "totalPrice": total,
                "amountPaid": total,
                "change": 0,
                "paymentDate": order.get("updatedAt", order.get("createdAt", datetime.now().isoformat())),
                "paymentMethod": order.get("paymentMethod", "Tunai")
            }

        return {
            "receiptId": payment.get("paymentId", f"REC-{order_id[-6:]}"),
            "orderId": order_id,
            "customerName": order.get("customerName", "-"),
            "tableNumber": order.get("tableNumber", "-"),
            "items": order.get("items", []),
            "totalPrice": payment.get("totalPrice", order.get("totalAmount", 0)),
            "amountPaid": payment.get("amountPaid", order.get("totalAmount", 0)),
            "change": payment.get("change", 0),
            "paymentDate": payment.get("paymentDate", datetime.now().isoformat()),
            "paymentMethod": order.get("paymentMethod", "Tunai")
        }