from fastapi import APIRouter, Depends, HTTPException
from app.controllers.kitchen_controller import KitchenController
from app.config.database import get_db

router = APIRouter(prefix="/kitchen", tags=["Kitchen"])

def get_kitchen_controller(db=Depends(get_db)):
    return KitchenController(db)


@router.get("/orders/pending")
async def get_pending_orders(controller: KitchenController = Depends(get_kitchen_controller)):
    """Kitchen melihat order yang pending"""
    orders = await controller.get_pending_orders()
    return {"success": True, "data": orders}


@router.get("/orders/cooking")
async def get_cooking_orders(controller: KitchenController = Depends(get_kitchen_controller)):
    """Kitchen melihat order yang sedang dimasak"""
    orders = await controller.get_cooking_orders()
    return {"success": True, "data": orders}


@router.put("/order/{order_id}/start")
async def start_cooking(
    order_id: str,
    controller: KitchenController = Depends(get_kitchen_controller)
):
    """Kitchen mulai memasak order"""
    try:
        order = await controller.start_cooking(order_id)
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        return {"success": True, "data": order}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/order/{order_id}/done")
async def done_cooking(
    order_id: str,
    controller: KitchenController = Depends(get_kitchen_controller)
):
    """Kitchen selesai memasak order"""
    try:
        order = await controller.done_cooking(order_id)
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        return {"success": True, "data": order}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))