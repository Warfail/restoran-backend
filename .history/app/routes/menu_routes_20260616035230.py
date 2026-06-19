from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime
from bson import ObjectId  # ← import ini
from app.config.database import get_db

router = APIRouter(prefix="/menu", tags=["Menu"])

from app.schemas.menu_schema import MenuCreate

@router.post("/")
async def create_menu(menu_data: MenuCreate, db = Depends(get_db)):
    menu_dict = menu_data.dict()
    menu_dict["createdAt"] = datetime.now()
    menu_dict["updatedAt"] = datetime.now()
    
    result = await db.menus.insert_one(menu_dict)
    menu_dict["_id"] = str(result.inserted_id)
    
    return {"success": True, "data": menu_dict}

@router.get("/")
async def get_all_menus(db = Depends(get_db)):
    cursor = db.menus.find({})
    menus = await cursor.to_list(length=100)
    for menu in menus:
        menu["_id"] = str(menu["_id"])
    return {"success": True, "data": menus}

@router.get("/{menu_id}")
async def get_menu(menu_id: str, db = Depends(get_db)):
    # Cari pakai _id
    if not ObjectId.is_valid(menu_id):
        raise HTTPException(status_code=400, detail="Invalid menu ID")
    
    menu = await db.menus.find_one({"_id": ObjectId(menu_id)})
    if not menu:
        raise HTTPException(status_code=404, detail="Menu not found")
    menu["_id"] = str(menu["_id"])
    return {"success": True, "data": menu}

@router.put("/{menu_id}")
async def update_menu(menu_id: str, menu_data: dict, db = Depends(get_db)):
    # Validasi ObjectId
    if "price" in menu_data:
        menu_data["price"] = int(menu_data["price"])
    if "stock" in menu_data:
        menu_data["stock"] = int(menu_data["stock"])
    if not ObjectId.is_valid(menu_id):
        raise HTTPException(status_code=400, detail="Invalid menu ID")
    
    # Remove fields yang ga boleh diupdate
    menu_data.pop("_id", None)
    menu_data.pop("menuId", None)
    menu_data["updatedAt"] = datetime.now()
    
    result = await db.menus.update_one(
        {"_id": ObjectId(menu_id)},  # ← cari pakai _id
        {"$set": menu_data}
    )
    
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Menu not found")
    
    return {"success": True, "message": "Menu updated"}

@router.delete("/{menu_id}")
async def delete_menu(menu_id: str, db = Depends(get_db)):
    if not ObjectId.is_valid(menu_id):
        raise HTTPException(status_code=400, detail="Invalid menu ID")
    
    result = await db.menus.delete_one({"_id": ObjectId(menu_id)})
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Menu not found")
    
    return {"success": True, "message": "Menu deleted"}