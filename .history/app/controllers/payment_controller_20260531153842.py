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
        
        total = order["totalPrice"]
        
        if amount_paid < total:
            return {"success": False, "message": "Uang kurang"}
        
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