from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime
from app.controllers.order_controller import OrderController
from app.controllers.payment_controller import PaymentController
from app.config.database import get_db
from app.utils import parse_json

router = APIRouter(prefix="/cashier", tags=["Cashier"])

def get_order_controller(db=Depends(get_db)):
    return OrderController(db)

def get_payment_controller(db=Depends(get_db)):
    return PaymentController(db)


# ========== TAMBAHKAN INI ==========
@router.get("/orders")
async def get_all_orders(db = Depends(get_db)):
    """
    Kasir melihat SEMUA order (pending + paid + cooking + completed)
    """
    try:
        cursor = db.orders.find({}).sort("createdAt", -1)
        orders = await cursor.to_list(length=None)
        
        for order in orders:
            order["_id"] = str(order["_id"])
            if "createdAt" in order and isinstance(order["createdAt"], datetime):
                order["createdAt"] = order["createdAt"].isoformat()
            if "updatedAt" in order and isinstance(order["updatedAt"], datetime):
                order["updatedAt"] = order["updatedAt"].isoformat()
        
        return {"success": True, "data": orders}
    except Exception as e:
        print("Error in get_all_orders:", e)
        return {"success": False, "error": str(e), "data": []}


@router.get("/orders/ongoing")
async def get_ongoing_orders(db = Depends(get_db)):
    """
    Kasir melihat order yang ONGOING (pending + paid + cooking)
    """
    try:
        cursor = db.orders.find({
            "status": {"$in": ["pending", "paid", "cooking"]}
        }).sort("createdAt", -1)
        orders = await cursor.to_list(length=100)
        
        for order in orders:
            order["_id"] = str(order["_id"])
            if "createdAt" in order and isinstance(order["createdAt"], datetime):
                order["createdAt"] = order["createdAt"].isoformat()
            if "updatedAt" in order and isinstance(order["updatedAt"], datetime):
                order["updatedAt"] = order["updatedAt"].isoformat()
        
        return {"success": True, "data": orders}
    except Exception as e:
        print("Error in get_ongoing_orders:", e)
        return {"success": False, "error": str(e), "data": []}


@router.post("/orders/cleanup_unprinted")
async def cleanup_unprinted(db = Depends(get_db)):
    """
    Temporary endpoint to mark all completed orders as printed.
    """
    try:
        result = await db.orders.update_many(
            {"status": "completed", "isPrinted": {"$ne": True}},
            {"$set": {"isPrinted": True}}
        )
        return {"success": True, "modified_count": result.modified_count}
    except Exception as e:
        return {"success": False, "error": str(e)}


# ========== ENDPOINT YANG UDAH ADA ==========
@router.get("/order/{order_id}")
async def get_order_detail(
    order_id: str,
    controller: OrderController = Depends(get_order_controller)
):
    """Kasir melihat detail order"""
    order = await controller.get_order(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return {"success": True, "data": parse_json(order)}


@router.put("/order/{order_id}/confirm")
async def confirm_order(
    order_id: str,
    db = Depends(get_db)
):
    """Kasir mengkonfirmasi pesanan"""
    # Cek order
    order = await db.orders.find_one({"orderId": order_id})
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # Update status
    await db.orders.update_one(
        {"orderId": order_id},
        {"$set": {
            "status": "paid",
            "payment_status": "paid",
            "updatedAt": datetime.now().isoformat()
        }}
    )
    
    # Update payments
    await db.payments.update_one(
        {"orderId": order_id},
        {"$set": {
            "status": "paid",
            "payment_status": "paid",
            "updatedAt": datetime.now().isoformat()
        }},
        upsert=True
    )
    
    return {"success": True, "message": "Payment confirmed"}

@router.put("/order/{order_id}/status")
async def update_order_status(
    order_id: str,
    status_data: dict,
    db = Depends(get_db)
):
    """Kasir update status order"""
    new_status = status_data.get("status")
    
    if new_status not in ["paid", "completed"]:
        raise HTTPException(status_code=400, detail="Invalid status. Use 'paid' or 'completed'")
    
    try:
        controller = get_order_controller(db)
        await controller.update_status(order_id, new_status)
        return {"success": True, "message": f"Order status updated to {new_status}"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/order/{order_id}/printed")
async def mark_order_printed(order_id: str, db = Depends(get_db)):
    """Tandai order sudah dicetak struknya"""
    result = await db.orders.update_one(
        {"orderId": order_id},
        {"$set": {"isPrinted": True, "updatedAt": datetime.now().isoformat()}}
    )
    if result.modified_count == 0:
        return {"success": False, "message": "Order not found or already marked"}
    return {"success": True, "message": "Order marked as printed"}




@router.post("/payment")
async def process_payment(
    order_id: str,
    amount_paid: float,
    controller: PaymentController = Depends(get_payment_controller)
):
    """Kasir memproses pembayaran"""
    result = await controller.process_payment(order_id, amount_paid)
    if not result:
        raise HTTPException(status_code=404, detail="Order not found")
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("message"))
    return parse_json(result)


@router.get("/receipt/{order_id}")
async def get_receipt(
    order_id: str,
    controller: PaymentController = Depends(get_payment_controller)
):
    """Kasir mencetak struk"""
    receipt = await controller.get_receipt(order_id)
    if not receipt:
        raise HTTPException(status_code=404, detail="Receipt not found")
    return {"success": True, "data": parse_json(receipt)}