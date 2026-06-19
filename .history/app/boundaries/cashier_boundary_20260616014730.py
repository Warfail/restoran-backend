from fastapi import APIRouter, Depends, HTTPException
from app.controllers.order_controller import OrderController
from app.controllers.payment_controller import PaymentController
from app.config.database import get_db
from app.utils import parse_json

@router.get("/order/{order_id}")
async def get_order_detail(order_id: str, controller: OrderController = Depends(get_order_controller)):
    order = await controller.get_order(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return {"success": True, "data": parse_json(order)}

router = APIRouter(prefix="/cashier", tags=["Cashier"])

def get_order_controller(db=Depends(get_db)):
    return OrderController(db)

def get_payment_controller(db=Depends(get_db)):
    return PaymentController(db)


@router.get("/orders")
async def get_all_orders(controller: OrderController = Depends(get_order_controller)):
    """Kasir melihat semua order"""
    orders = await controller.get_all_orders()
    return {"success": True, "data": orders}


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
    controller: OrderController = Depends(get_order_controller)
):
    """Kasir mengkonfirmasi pesanan (stok berkurang)"""
    try:
        order = await controller.confirm_order(order_id)
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        return {"success": True, "data": parse_json(order)}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


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