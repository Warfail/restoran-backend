from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime
from bson import ObjectId  # ← import ini
from app.config.database import get_db

router = APIRouter(prefix="/menu", tags=["Menu"])

from app.schemas.menu_schema import MenuCreate

@router.post("/")
async def create_menu(menu_data: dict, db = Depends(get_db)):
    # TERIMA SEBAGAI DICT, BUKAN PYDANTIC
    
    # PAKSA KONVERSI KE INTEGER
    raw_price = menu_data.get("price", 0)
    raw_stock = menu_data.get("stock", 0)
    
    # Konversi manual
    try:
        final_price = int(float(str(raw_price))) if raw_price else 0
    except:
        final_price = 0
    
    try:
        final_stock = int(float(str(raw_stock))) if raw_stock else 0
    except:
        final_stock = 0
    
    # Buat data baru dengan tipe yang benar
    menu_dict = {
        "name": str(menu_data.get("name", "")),
        "category": str(menu_data.get("category", "")),
        "price": final_price,           # ← integer
        "stock": final_stock,            # ← integer
        "description": str(menu_data.get("description", "")),
        "isAvailable": bool(menu_data.get("isAvailable", True)),
        "image": str(menu_data.get("image", "https://placehold.co/100x80/c8a96e/c8a96e")),
        "createdAt": datetime.now(),
        "updatedAt": datetime.now()
    }
    
    print(f"📦 SAVING: price={final_price} (type: {type(final_price)}), stock={final_stock} (type: {type(final_stock)})")
    
    result = await db.menus.insert_one(menu_dict)
    menu_dict["_id"] = str(result.inserted_id)
    
    return {"success": True, "data": menu_dict}

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