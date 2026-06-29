from fastapi import APIRouter, HTTPException, Depends
from datetime import datetime
import midtransclient
import os
import hashlib
import hmac
from app.config.database import get_db
from app.utils import serialize_document, serialize_list, serialize_value

router = APIRouter(prefix="/payment", tags=["Payment"])

# Init Midtrans Snap client
snap = midtransclient.Snap(
    is_production=os.getenv("MIDTRANS_IS_PRODUCTION", "false").lower() == "true",
    server_key=os.getenv("MIDTRANS_SERVER_KEY"),
    client_key=os.getenv("MIDTRANS_CLIENT_KEY"),
)

@router.post("/create-transaction")
async def create_transaction(order_data: dict, db=Depends(get_db)):
    """
    Create Midtrans transaction and return Snap token
    """
    order_id = order_data.get("orderId")
    gross_amount = order_data.get("totalAmount")
    customer_name = order_data.get("customerName", "Guest")
    customer_email = order_data.get("customerEmail", "guest@example.com")
    
    # Check order exists
    order = await db.orders.find_one({"orderId": order_id})
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
        
    server_key = os.getenv("MIDTRANS_SERVER_KEY")
    if not server_key or server_key == "YOUR_SERVER_KEY":
        raise HTTPException(status_code=500, detail="Server Key Midtrans belum dikonfigurasi di .env backend")
    
    # Build param untuk Midtrans
    param = {
        "transaction_details": {
            "order_id": order_id,
            "gross_amount": gross_amount,
        },
        "customer_details": {
            "first_name": customer_name,
            "email": customer_email,
        },
        "item_details": [
            {
                "id": item.get("menuId", f"item-{idx}"),
                "price": item.get("price", 0),
                "quantity": item.get("quantity", 1),
                "name": item.get("name", "Menu"),
            }
            for idx, item in enumerate(order.get("items", []))
        ],
        "enabled_payments": [
            "credit_card",
            "bank_transfer_bca",
            "bank_transfer_bni",
            "bank_transfer_bri",
            "bank_transfer_permata",
            "gopay",
            "qris",
        ],
    }
    
    try:
        # Create transaction ke Midtrans
        response = snap.create_transaction(param)
        token = response["token"]
        redirect_url = response["redirect_url"]
        
        # Simpan token ke order di database
        await db.orders.update_one(
            {"orderId": order_id},
            {"$set": {
                "midtrans_token": token,
                "midtrans_redirect_url": redirect_url,
                "payment_status": "pending",
            }}
        )
        
        return {
            "success": True,
            "token": token,
            "redirect_url": redirect_url,
        }
    except Exception as e:
        print("Midtrans Error:", str(e))
        raise HTTPException(status_code=500, detail=f"Payment gateway error: {str(e)}")


@router.post("/notification")
async def payment_notification(notification_data: dict, db=Depends(get_db)):
    """
    Handle webhook notification dari Midtrans
    """
    try:
        order_id = notification_data.get("order_id")
        transaction_status = notification_data.get("transaction_status")
        status_code = notification_data.get("status_code")
        gross_amount = notification_data.get("gross_amount")
        signature_key = notification_data.get("signature_key")
        
        # 🔥 VERIFIKASI SIGNATURE (Keamanan)
        server_key = os.getenv("MIDTRANS_SERVER_KEY")
        expected_signature = hashlib.sha256(
            f"{order_id}{status_code}{gross_amount}{server_key}".encode()
        ).hexdigest()
        
        if signature_key != expected_signature:
            print("⚠️ Invalid signature!")
            return {"success": False, "error": "Invalid signature"}
        
        # Update order status berdasarkan transaction_status
        new_status = "pending"
        if transaction_status == "settlement":
            new_status = "paid"
        elif transaction_status == "expire":
            new_status = "expired"
        elif transaction_status == "cancel":
            new_status = "cancelled"
        elif transaction_status == "pending":
            new_status = "pending"
        
        # Update status payment khusus midtrans dulu
        await db.orders.update_one(
            {"orderId": order_id},
            {"$set": {
                "payment_status": transaction_status,
                "payment_updated_at": datetime.now().isoformat(),
            }}
        )
        
        # Gunakan OrderController agar logika potong stok dll tetap berjalan
        from app.controllers.order_controller import OrderController
        order_ctrl = OrderController(db)
        await order_ctrl.update_status(order_id, new_status)
        
        print(f"✅ Payment notification: {order_id} -> {new_status}")
        return {"success": True}
    except Exception as e:
        print("Webhook error:", str(e))
        return {"success": False, "error": str(e)}


@router.post("/set-method")
async def set_payment_method(data: dict, db=Depends(get_db)):
    """
    Set payment method untuk order (cash/debit)
    """
    order_id = data.get("orderId")
    method = data.get("method")
    
    if not order_id or not method:
        raise HTTPException(status_code=400, detail="orderId and method are required")
    
    # Check order exists
    order = await db.orders.find_one({"orderId": order_id})
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # Update payment method
    await db.orders.update_one(
        {"orderId": order_id},
        {"$set": {
            "payment_method": method,
            "payment_status": "pending_cash" if method in ["cash", "debit"] else "pending",
            "payment_updated_at": datetime.now().isoformat(),
        }}
    )
    
    return {"success": True, "message": f"Payment method set to {method}"}