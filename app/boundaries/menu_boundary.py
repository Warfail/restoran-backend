from fastapi import APIRouter, Depends, HTTPException
from app.controllers.menu_controller import MenuController
from app.config.database import get_db

router = APIRouter(prefix="/menu", tags=["Menu"])

def get_menu_controller(db=Depends(get_db)):
    return MenuController(db)


@router.get("/")
async def get_all_menu(controller: MenuController = Depends(get_menu_controller)):
    """Get all menu items"""
    menus = await controller.get_all_menu()
    return {"success": True, "data": menus}


@router.get("/available")
async def get_available_menu(controller: MenuController = Depends(get_menu_controller)):
    """Get available menu items (in stock)"""
    menus = await controller.get_available_menu()
    return {"success": True, "data": menus}


@router.get("/{menu_id}")
async def get_menu_by_id(
    menu_id: str, 
    controller: MenuController = Depends(get_menu_controller)
):
    """Get menu item by ID"""
    menu = await controller.get_menu_by_id(menu_id)
    if not menu:
        raise HTTPException(status_code=404, detail="Menu not found")
    return {"success": True, "data": menu}


@router.post("/")
async def create_menu(
    menu_data: dict,
    controller: MenuController = Depends(get_menu_controller)
):
    """Create new menu item"""
    menu = await controller.create_menu(menu_data)
    return {"success": True, "data": menu}