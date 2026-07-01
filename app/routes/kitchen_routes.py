from fastapi import APIRouter, HTTPException, Depends
from datetime import datetime
from app.config.database import get_db
from app.utils import serialize_document, serialize_list, serialize_value

router = APIRouter(prefix="/kitchen", tags=["Kitchen"])

# NOTE: /orders/count MUST be declared BEFORE /orders/{order_id} to avoid
# FastAPI matching "count" as a path parameter.
@router.get("/orders/count")
async def get_kitchen_order_count(db = Depends(get_db)):
    """
    Returns order counts for 'paid' and 'cooking' statuses in a single
    aggregation pipeline instead of two separate count_documents calls.
    """
    pipeline = [
        {"$match": {"status": {"$in": ["paid", "cooking"]}}},
        {"$group": {"_id": "$status", "count": {"$sum": 1}}}
    ]
    results = await db.orders.aggregate(pipeline).to_list(length=10)
    counts = {row["_id"]: row["count"] for row in results}
    paid_count = counts.get("paid", 0)
    cooking_count = counts.get("cooking", 0)

    return {
        "success": True,
        "data": {
            "antrean": paid_count,
            "dimasak": cooking_count,
            "total": paid_count + cooking_count
        }
    }

@router.get("/orders")
async def get_kitchen_orders(db = Depends(get_db)):
    """
    Fetch active kitchen orders (paid/cooking), sorted by creation time (FIFO).
    Only the fields needed by the kitchen are projected to reduce payload size.
    """
    orders = await db.orders.find(
        {"status": {"$in": ["paid", "cooking"]}},
        # Project only the fields the kitchen dashboard uses
        projection={
            "orderId": 1, "tableNumber": 1, "customerName": 1,
            "status": 1, "items": 1, "createdAt": 1, "updatedAt": 1
        }
    ).sort("createdAt", 1).to_list(length=200)

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
        from app.routes.inventory_routes import reduce_stock
        await reduce_stock({"orderId": order_id, "items": order.get("items", [])}, db)

    result = await db.orders.update_one(
        {"orderId": order_id},
        {"$set": {"status": new_status, "updatedAt": datetime.now().isoformat()}}
    )

    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Order not found")

    return {"success": True, "message": f"Order status updated to {new_status}"}