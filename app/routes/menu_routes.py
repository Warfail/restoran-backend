from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime
from bson import ObjectId
from app.config.database import get_db
from app.utils import serialize_document, serialize_list, serialize_value

router = APIRouter(prefix="/menu", tags=["Menu"])

@router.post("/")
async def create_menu(menu_data: dict, db = Depends(get_db)):
    # PASTIKAN TIPE DATA
    try:
        price = int(menu_data.get("price", 0))
    except:
        price = 0
    
    try:
        stock = int(menu_data.get("stock", 0))
    except:
        stock = 0
    
    menu_dict = {
        "name": str(menu_data.get("name", "")),
        "category": str(menu_data.get("category", "")),
        "price": price,
        "stock": stock,
        "description": str(menu_data.get("description", "")),
        "isAvailable": bool(menu_data.get("isAvailable", True)),
        "image": str(menu_data.get("image", "https://placehold.co/100x80/c8a96e/c8a96e")),
        "recipe": menu_data.get("recipe", []),
        "createdAt": datetime.now(),
        "updatedAt": datetime.now()
    }
    
    print(f"✅ SAVING: price={price} ({type(price).__name__}), stock={stock} ({type(stock).__name__})")
    
    result = await db.menus.insert_one(menu_dict)
    menu_dict["_id"] = str(result.inserted_id)
    
    return {"success": True, "data": menu_dict}

@router.get("/")
async def get_all_menus(limit: int = 30, db = Depends(get_db)):
    """
    Get all menus with limit (default 30)
    """
    cursor = db.menus.find({}).limit(limit)
    menus = await cursor.to_list(length=limit)
    for menu in menus:
        menu["_id"] = str(menu["_id"])
    return {"success": True, "data": menus}

@router.get("/{menu_id}")
async def get_menu(menu_id: str, db = Depends(get_db)):
    # Coba cari berdasarkan menuId dulu
    menu = await db.menus.find_one({"menuId": menu_id})
    if not menu:
        # Kalo ga ketemu, coba sebagai ObjectId
        try:
            menu = await db.menus.find_one({"_id": ObjectId(menu_id)})
        except:
            pass
    
    if not menu:
        raise HTTPException(status_code=404, detail="Menu not found")
    
    menu["_id"] = str(menu["_id"])
    return {"success": True, "data": menu}

@router.put("/{menu_id}")
async def update_menu(menu_id: str, menu_data: dict, db = Depends(get_db)):
    # Coba cari berdasarkan menuId dulu
    query = {"menuId": menu_id}
    menu = await db.menus.find_one(query)
    if not menu:
        try:
            query = {"_id": ObjectId(menu_id)}
            menu = await db.menus.find_one(query)
        except:
            pass
    
    if not menu:
        raise HTTPException(status_code=404, detail="Menu not found")
    
    # 🔥 HAPUS field yang ga boleh di-update
    menu_data.pop("_id", None)
    menu_data.pop("menuId", None)
    menu_data.pop("createdAt", None)
    
    # 🔥 Tambah updatedAt
    menu_data["updatedAt"] = datetime.now()
    
    # 🔥 UPDATE!
    result = await db.menus.update_one(
        query,
        {"$set": menu_data}
    )
    
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Menu not found")
    
    return {"success": True, "message": "Menu updated"}

@router.delete("/{menu_id}")
async def delete_menu(menu_id: str, db = Depends(get_db)):
    # Coba cari berdasarkan menuId dulu
    query = {"menuId": menu_id}
    menu = await db.menus.find_one(query)
    if not menu:
        try:
            query = {"_id": ObjectId(menu_id)}
            menu = await db.menus.find_one(query)
        except:
            pass
    
    if not menu:
        raise HTTPException(status_code=404, detail="Menu not found")
    
    result = await db.menus.delete_one(query)
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Menu not found")
    
    return {"success": True, "message": "Menu deleted"}