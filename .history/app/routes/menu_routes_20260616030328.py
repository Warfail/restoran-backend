from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime
import uuid
from app.config.database import get_db

router = APIRouter(prefix="/menu", tags=["Menu"])

@router.post("/")
async def create_menu(menu_data: dict, db = Depends(get_db)):
    # Generate menuId unik
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    random_suffix = str(uuid.uuid4().hex[:4]).upper()
    menu_data["menuId"] = f"MENU{timestamp}{random_suffix}"
    
    # Set default values if not provided
    if "isAvailable" not in menu_data:
        menu_data["isAvailable"] = True
    if "stock" not in menu_data:
        menu_data["stock"] = 0
    if "createdAt" not in menu_data:
        menu_data["createdAt"] = datetime.now()
    
    result = await db.menus.insert_one(menu_data)
    menu_data["_id"] = str(result.inserted_id)
    
    return {"success": True, "data": menu_data}

@router.get("/")
async def get_all_menus(db = Depends(get_db)):
    cursor = db.menus.find({})
    menus = await cursor.to_list(length=100)
    for menu in menus:
        menu["_id"] = str(menu["_id"])
    return {"success": True, "data": menus}

@router.get("/{menu_id}")
async def get_menu(menu_id: str, db = Depends(get_db)):
    menu = await db.menus.find_one({"menuId": menu_id})
    if not menu:
        raise HTTPException(status_code=404, detail="Menu not found")
    menu["_id"] = str(menu["_id"])
    return {"success": True, "data": menu}

@router.put("/{menu_id}")
async def update_menu(menu_id: str, menu_data: dict, db = Depends(get_db)):
    # Remove _id from update data if exists
    menu_data.pop("_id", None)
    menu_data.pop("menuId", None)
    menu_data["updatedAt"] = datetime.now()
    
    result = await db.menus.update_one(
        {"menuId": menu_id},
        {"$set": menu_data}
    )
    
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Menu not found")
    
    return {"success": True, "message": "Menu updated"}

@router.delete("/{menu_id}")
async def delete_menu(menu_id: str, db = Depends(get_db)):
    result = await db.menus.delete_one({"menuId": menu_id})
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Menu not found")
    
    return {"success": True, "message": "Menu deleted"}