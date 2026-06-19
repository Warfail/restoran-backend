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