from fastapi import APIRouter, HTTPException, Depends
from datetime import datetime
from app.config.database import get_db
from app.utils import serialize_document, serialize_list, serialize_value

router = APIRouter(prefix="/kitchen", tags=["Kitchen"])

@router.get("/orders")
async def get_kitchen_orders(db = Depends(get_db)):
    orders = await db.orders.find({
        "status": {"$in": ["paid", "cooking"]}
    }).to_list(length=100)
    
    for order in orders:
        order["_id"] = str(order["_id"])
        if "createdAt" in order and isinstance(order["createdAt"], datetime):
            order["createdAt"] = order["createdAt"].isoformat()
    
    return {"success": True, "data": orders}

@router.put("/orders/{order_id}/status")
async def update_kitchen_order_status(order_id: str, status_data: dict, db = Depends(get_db)):
    new_status = status_data.get("status")
    
    if new_status not in ["cooking", "completed"]:
        raise HTTPException(status_code=400, detail="Invalid status. Use 'cooking' or 'completed'")
    
    order = await db.orders.find_one({"orderId": order_id})
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # 🔥 Jika status berubah ke "cooking", kurangi stok
    if new_status == "cooking" and order["status"] != "cooking":
        # Panggil fungsi reduce_stock
        from app.routes.inventory_routes import reduce_stock
        await reduce_stock({"orderId": order_id, "items": order.get("items", [])}, db)
    
    result = await db.orders.update_one(
        {"orderId": order_id},
        {"$set": {"status": new_status, "updatedAt": datetime.now().isoformat()}}
    )
    
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Order not found")
    
    return {"success": True, "message": f"Order status updated to {new_status}"}

@router.get("/orders/count")
async def get_kitchen_order_count(db = Depends(get_db)):
    paid_count = await db.orders.count_documents({"status": "paid"})
    cooking_count = await db.orders.count_documents({"status": "cooking"})
    
    return {
        "success": True,
        "data": {
            "antrean": paid_count,
            "dimasak": cooking_count,
            "total": paid_count + cooking_count
        }
    }