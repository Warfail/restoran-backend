from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime
from bson import ObjectId
from app.config.database import get_db

router = APIRouter(prefix="/menu", tags=["Menu"])

@router.post("/")
async def create_menu(menu_data: dict, db = Depends(get_db)):
    # PASTIKAN TYPE DATA
    menu_data["name"] = str(menu_data.get("name", ""))
    menu_data["category"] = str(menu_data.get("category", ""))
    menu_data["price"] = int(menu_data.get("price", 0))  # ← konversi ke int
    menu_data["stock"] = int(menu_data.get("stock", 0))  # ← konversi ke int
    menu_data["description"] = str(menu_data.get("description", ""))
    menu_data["isAvailable"] = bool(menu_data.get("isAvailable", True))
    
    # Timestamps
    if "createdAt" not in menu_data:
        menu_data["createdAt"] = datetime.now()
    if "updatedAt" not in menu_data:
        menu_data["updatedAt"] = datetime.now()
    
    # Image default
    if "image" not in menu_data or not menu_data["image"]:
        menu_data["image"] = "https://placehold.co/100x80/c8a96e/c8a96e"
    
    result = await db.menus.insert_one(menu_data)
    menu_data["_id"] = str(result.inserted_id)
    
    return {"success": True, "data": menu_data}

@router.get("/")
async def get_all_menus(db = Depends(get_db)):
    cursor = db.menus.find({})
    menus = await cursor.to_list(length=100)
    for menu in menus:
        menu["_id"] = str(menu["_id"])
        # Pastikan type data number
        menu["price"] = int(menu.get("price", 0))
        menu["stock"] = int(menu.get("stock", 0))
    return {"success": True, "data": menus}

@router.get("/{menu_id}")
async def get_menu(menu_id: str, db = Depends(get_db)):
    if not ObjectId.is_valid(menu_id):
        raise HTTPException(status_code=400, detail="Invalid menu ID")
    
    menu = await db.menus.find_one({"_id": ObjectId(menu_id)})
    if not menu:
        raise HTTPException(status_code=404, detail="Menu not found")
    
    menu["_id"] = str(menu["_id"])
    menu["price"] = int(menu.get("price", 0))
    menu["stock"] = int(menu.get("stock", 0))
    
    return {"success": True, "data": menu}

@router.put("/{menu_id}")
async def update_menu(menu_id: str, menu_data: dict, db = Depends(get_db)):
    if not ObjectId.is_valid(menu_id):
        raise HTTPException(status_code=400, detail="Invalid menu ID")
    
    # Remove fields yang ga boleh diupdate
    menu_data.pop("_id", None)
    menu_data.pop("createdAt", None)  # createdAt ga boleh berubah
    
    # Konversi type data
    if "price" in menu_data:
        menu_data["price"] = int(menu_data["price"])
    if "stock" in menu_data:
        menu_data["stock"] = int(menu_data["stock"])
    if "isAvailable" in menu_data:
        menu_data["isAvailable"] = bool(menu_data["isAvailable"])
    
    # Update timestamp
    menu_data["updatedAt"] = datetime.now()
    
    result = await db.menus.update_one(
        {"_id": ObjectId(menu_id)},
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