from fastapi import APIRouter, Depends, HTTPException
from app.controllers.order_controller import OrderController
from app.controllers.menu_controller import MenuController
from app.config.database import get_db

router = APIRouter(prefix="/order", tags=["Order"])

def get_order_controller(db=Depends(get_db)):
    return OrderController(db)

def get_menu_controller(db=Depends(get_db)):
    return MenuController(db)


@router.post("/")
async def create_order(
    customer_name: str,
    table_number: int,
    controller: OrderController = Depends(get_order_controller)
):
    order = await controller.create_order(customer_name, table_number)
    return {"success": True, "data": order}


@router.post("/{order_id}/items")
async def add_order_item(
    order_id: str,
    menu_id: str,
    quantity: int,
    order_controller: OrderController = Depends(get_order_controller),
    menu_controller: MenuController = Depends(get_menu_controller)
):
    order = await order_controller.add_item(order_id, menu_id, quantity, menu_controller.menu_repo)
    if not order:
        raise HTTPException(status_code=404, detail="Order or Menu not found")
    return {"success": True, "data": order}


@router.get("/{order_id}")
async def get_order(
    order_id: str,
    controller: OrderController = Depends(get_order_controller)
):
    order = await controller.get_order(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return {"success": True, "data": order}