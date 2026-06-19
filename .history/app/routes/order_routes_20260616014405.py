from fastapi import APIRouter, HTTPException, Depends
from datetime import datetime
import uuid
from app.config.database import get_db

router = APIRouter()

@router.post("/orders")
async def create_order(order_data: dict, db = Depends(get_db)):
    # db langsung siap pakai karena Depends(get_db) akan handle await
    new_order = {
        "orderId": f"ORD-{uuid.uuid4().hex[:8].upper()}",
        "customerName": order_data.get("customerName"),
        "tableNumber": order_data.get("tableNumber"),
        "orderType": order_data.get("orderType"),
        "items": order_data.get("items", []),
        "totalAmount": order_data.get("totalAmount"),
        "status": "pending",
        "createdAt": datetime.now()
    }
    
    result = await db.orders.insert_one(new_order)
    new_order["_id"] = str(result.inserted_id)
    
    return {"success": True, "data": new_order}

@router.get("/orders/{order_id}")
async def get_order(order_id: str, db = Depends(get_db)):
    order = await db.orders.find_one({"orderId": order_id})
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    order["_id"] = str(order["_id"])
    return {"success": True, "data": order}

@router.post("/payments")
async def process_payment(payment_data: dict, db = Depends(get_db)):
    print("Received payment data:", payment_data)  # Debug
    
    order_id = payment_data.get("orderId")  # Pake .get() biar aman
    if not order_id:
        raise HTTPException(status_code=400, detail="orderId is required")
    
    # Update status order jadi paid
    result = await db.orders.update_one(
        {"orderId": order_id},
        {"$set": {"status": "paid", "paymentMethod": payment_data.get("method")}}
    )
    
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Order not found")
    
    return {"success": True, "message": "Payment successful"}

@router.put("/orders/{order_id}/confirm-payment")
async def confirm_payment(order_id: str, db = Depends(get_db)):
    # Update status dari pending ke paid
    result = await db.orders.update_one(
        {"orderId": order_id, "status": "pending"},
        {"$set": {"status": "paid"}}
    )
    
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Order not found or already paid")
    
    return {"success": True, "message": "Payment confirmed"}