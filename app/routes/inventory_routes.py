from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime
from bson import ObjectId
from app.config.database import get_db
from app.utils.serializers import serialize_document, serialize_list, serialize_value

router = APIRouter(prefix="/inventory", tags=["Inventory"])

@router.get("/")
async def get_all_inventory(db = Depends(get_db)):
    cursor = db.inventory.find({})
    items = await cursor.to_list(length=100)
    for item in items:
        item["_id"] = str(item["_id"])
    return {"success": True, "data": items}

@router.get("/{item_id}")
async def get_inventory_item(item_id: str, db = Depends(get_db)):
    if not ObjectId.is_valid(item_id):
        raise HTTPException(status_code=400, detail="Invalid ID")
    
    item = await db.inventory.find_one({"_id": ObjectId(item_id)})
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    item["_id"] = str(item["_id"])
    return {"success": True, "data": item}

@router.post("/")
async def create_inventory_item(item_data: dict, db = Depends(get_db)):
    # Konversi stock ke integer
    try:
        stock = int(item_data.get("stock", 0))
    except:
        stock = 0
    
    item_dict = {
        "name": str(item_data.get("name", "")),
        "stock": stock,
        "unit": str(item_data.get("unit", "unit")),
        "category": str(item_data.get("category", "Bahan Baku")),
        "minStock": int(item_data.get("minStock", 0)),
        "createdAt": datetime.now(),
        "updatedAt": datetime.now()
    }
    
    result = await db.inventory.insert_one(item_dict)
    item_dict["_id"] = str(result.inserted_id)
    
    return {"success": True, "data": item_dict}

@router.put("/{item_id}")
async def update_inventory_stock(item_id: str, update_data: dict, db = Depends(get_db)):
    if not ObjectId.is_valid(item_id):
        raise HTTPException(status_code=400, detail="Invalid ID")
    
    # Konversi stock ke integer
    if "stock" in update_data:
        try:
            update_data["stock"] = int(update_data["stock"])
        except:
            update_data["stock"] = 0
    
    update_data["updatedAt"] = datetime.now()
    update_data.pop("_id", None)
    
    result = await db.inventory.update_one(
        {"_id": ObjectId(item_id)},
        {"$set": update_data}
    )
    
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Item not found")
    
    return {"success": True, "message": "Stock updated"}

@router.delete("/{item_id}")
async def delete_inventory_item(item_id: str, db = Depends(get_db)):
    if not ObjectId.is_valid(item_id):
        raise HTTPException(status_code=400, detail="Invalid ID")
    
    result = await db.inventory.delete_one({"_id": ObjectId(item_id)})
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Item not found")
    
    return {"success": True, "message": "Item deleted"}


@router.post("/reduce")
async def reduce_stock(data: dict, db = Depends(get_db)):
    """
    Kurangi stok bahan berdasarkan recipe
    """
    try:
        order_id = data.get("orderId")
        
        if not order_id:
            raise HTTPException(status_code=400, detail="orderId is required")
        
        logs = []
        errors = []
        
        # Ambil order detail
        order = await db.orders.find_one({"orderId": order_id})
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        
        for item in order.get("items", []):
            menu_id = item.get("menuId")
            quantity = item.get("quantity", 1)
            
            # Cari menu
            menu = None
            if ObjectId.is_valid(menu_id):
                menu = await db.menus.find_one({"_id": ObjectId(menu_id)})
            if not menu:
                menu = await db.menus.find_one({"menuId": menu_id})
            
            if not menu:
                errors.append(f"Menu {menu_id} not found")
                continue
            
            recipe = menu.get("recipe", [])
            if not recipe:
                continue
            
            # Untuk setiap bahan di recipe
            for ingredient in recipe:
                ingredient_id = ingredient.get("ingredientId")
                ingredient_name = ingredient.get("name")
                ingredient_qty = ingredient.get("quantity", 0) * quantity
                unit = ingredient.get("unit", "unit")
                
                # Cari inventory
                inventory = await db.inventory.find_one({"ingredientId": ingredient_id})
                if not inventory:
                    inventory = await db.inventory.find_one({"name": ingredient_name})
                
                if not inventory:
                    errors.append(f"Ingredient {ingredient_name} not found in inventory")
                    continue
                
                # Cek stok cukup?
                if inventory["stock"] < ingredient_qty:
                    errors.append(f"Stok {ingredient_name} tidak cukup! Sisa: {inventory['stock']} {inventory['unit']}")
                    continue
                
                # Kurangi stok
                new_stock = inventory["stock"] - ingredient_qty
                await db.inventory.update_one(
                    {"_id": inventory["_id"]},
                    {"$set": {"stock": new_stock, "updatedAt": datetime.now().isoformat()}}
                )
                
                # 🔥 PAKE SERIALIZER
                log = {
                    "orderId": str(order_id),
                    "menuId": menu.get("menuId") or str(menu["_id"]),
                    "menuName": str(menu.get("name")),
                    "ingredientId": inventory.get("ingredientId") or str(inventory["_id"]),
                    "ingredientName": str(inventory.get("name")),
                    "quantity": float(ingredient_qty),
                    "unit": str(unit),
                    "action": "used",
                    "timestamp": datetime.now().isoformat(),
                    "remainingStock": float(new_stock),
                    "performedBy": "kitchen"
                }
                logs.append(log)
                await db.stock_logs.insert_one(log)
        
        # 🔥 Serialize semua data sebelum return
        serialized_logs = [serialize_document(log) for log in logs]
        serialized_errors = [str(e) for e in errors]
        
        return {
            "success": len(errors) == 0,
            "errors": serialized_errors,
            "logs": serialized_logs
        }
    except Exception as e:
        print(f"Error in reduce_stock: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))