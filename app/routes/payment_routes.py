from fastapi import APIRouter, HTTPException, Depends, Request
from datetime import datetime
import midtransclient
import os
import hashlib
import uuid
from app.config.database import get_db

# Tambahkan di awal file, setelah import
FRONTEND_URL = os.getenv("FRONTEND_URL", "https://restoran-frontend-nu.vercel.app/")

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
        "finish_redirect_url": f"{FRONTEND_URL}/order-status?orderId={order_id}",
        "unfinish_redirect_url": f"{FRONTEND_URL}/order-status?orderId={order_id}",
        "error_redirect_url": f"{FRONTEND_URL}/order-status?orderId={order_id}",
        "redirect_url": f"{FRONTEND_URL}/order-status?orderId={order_id}", 
    }
    
    try:
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
                "redirect_after_payment": f"/order-status?orderId={order_id}"
            }}
        )
        
        return {
            "success": True,
            "token": token,
            "redirect_url": redirect_url,
            "order_id": order_id,
        }
    except Exception as e:
        print("Midtrans Error:", str(e))
        raise HTTPException(status_code=500, detail=f"Payment gateway error: {str(e)}")

# ✅ WEBHOOK ENDPOINT
@router.post("/webhook")
async def payment_webhook(request: Request, db=Depends(get_db)):
    """
    Endpoint buat terima notifikasi dari Midtrans
    """
    # Ambil raw body
    payload = await request.json()
    
    # Log payload buat debugging
    print("Webhook received:", payload)
    
    # 1. VERIFIKASI SIGNATURE (keamanan!)
    order_id = payload.get("order_id")
    status_code = payload.get("status_code")
    gross_amount = payload.get("gross_amount")
    signature_key = payload.get("signature_key")
    
    # Dapatkan server_key dari environment
    server_key = os.getenv("MIDTRANS_SERVER_KEY")
    
    # Buat signature yang diharapkan
    expected_signature = hashlib.sha512(
        f"{order_id}{status_code}{gross_amount}{server_key}".encode()
    ).hexdigest()
    
    # Bandingkan dengan signature dari Midtrans
    if signature_key != expected_signature:
        print("❌ Invalid signature!")
        raise HTTPException(status_code=403, detail="Invalid signature")
    
    # 2. PROSES STATUS
    transaction_status = payload.get("transaction_status")
    fraud_status = payload.get("fraud_status")
    
    print(f"📦 Order: {order_id}, Status: {transaction_status}")
    
    # Update database berdasarkan status
    if transaction_status == "settlement":
        # ✅ Pembayaran berhasil!
        await db.orders.update_one(
            {"orderId": order_id},
            {"$set": {
                "payment_status": "paid",
                "payment_updated_at": datetime.now(),
                "midtrans_response": payload
            }}
        )
        print(f"✅ Payment SUCCESS for order {order_id}")
        
    elif transaction_status == "pending":
        # ⏳ Menunggu pembayaran
        await db.orders.update_one(
            {"orderId": order_id},
            {"$set": {
                "payment_status": "pending",
                "payment_updated_at": datetime.now(),
                "midtrans_response": payload
            }}
        )
        print(f"⏳ Payment PENDING for order {order_id}")
        
    elif transaction_status == "expire":
        # ⏰ Kadaluarsa
        await db.orders.update_one(
            {"orderId": order_id},
            {"$set": {
                "payment_status": "expired",
                "payment_updated_at": datetime.now(),
                "midtrans_response": payload
            }}
        )
        print(f"⏰ Payment EXPIRED for order {order_id}")
        
    elif transaction_status == "cancel":
        # ❌ Dibatalkan
        await db.orders.update_one(
            {"orderId": order_id},
            {"$set": {
                "payment_status": "cancelled",
                "payment_updated_at": datetime.now(),
                "midtrans_response": payload
            }}
        )
        print(f"❌ Payment CANCELLED for order {order_id}")
    
    # Selalu return 200 ke Midtrans
    return {"status": "ok"}

# ✅ LOCAL-SUCCESS ENDPOINT - HARUS DI LUAR FUNGSI WEBHOOK!
@router.post("/local-success")
async def local_payment_success(data: dict, db=Depends(get_db)):
    """
    Endpoint buat sync pembayaran dari frontend (fallback jika webhook lambat)
    """
    order_id = data.get("orderId")
    
    if not order_id:
        raise HTTPException(status_code=400, detail="orderId is required")
    
    # Cek apakah order ada
    order = await db.orders.find_one({"orderId": order_id})
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # Update status jadi paid (kalo masih pending)
    if order.get("payment_status") != "paid":
        await db.orders.update_one(
            {"orderId": order_id},
            {"$set": {
                "payment_status": "paid",
                "payment_updated_at": datetime.now(),
                "midtrans_response": {"source": "local-success-fallback"}
            }}
        )
        print(f"✅ Local success: Order {order_id} updated to paid")
    else:
        print(f"ℹ️ Local success: Order {order_id} already paid")
    
    return {"success": True, "order_id": order_id}