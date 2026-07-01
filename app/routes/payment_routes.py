from fastapi import APIRouter, HTTPException, Depends
from datetime import datetime
import midtransclient
import os
import hashlib
import uuid
from app.config.database import get_db

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