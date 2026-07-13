from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime
from bson import ObjectId
from app.config.database import get_db
from app.utils import serialize_document, serialize_list, serialize_value

router = APIRouter(prefix="/inventory", tags=["Inventory"])

@router.get("/")
async def get_all_inventory(db = Depends(get_db)):
    cursor = db.inventory.find({})
    items = await cursor.to_list(length=1000)
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
    # Konversi stock ke float agar tidak memotong desimal
    try:
        stock = float(item_data.get("stock", 0))
    except:
        stock = 0.0
    
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
    
    # Konversi stock ke float agar tidak memotong desimal
    if "stock" in update_data:
        try:
            update_data["stock"] = float(update_data["stock"])
        except:
            update_data["stock"] = 0.0
    
    update_data["updatedAt"] = datetime.now()
    update_data.pop("_id", None)
    
    result = await db.inventory.update_one(
        {"_id": ObjectId(item_id)},
        {"$set": update_data}
    )
    
    if result.matched_count == 0:
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
    Kurangi stok bahan berdasarkan recipe.
    Optimized: uses bulk $in queries instead of sequential find_one per item/ingredient.
    + Auto-disable menu jika bahan habis
    """
    import asyncio
    try:
        order_id = data.get("orderId")

        if not order_id:
            raise HTTPException(status_code=400, detail="orderId is required")

        logs = []
        errors = []
        disabled_menus = []  # 🔥 TAMBAHKAN

        # 1. Fetch order
        order = await db.orders.find_one({"orderId": order_id})
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")

        order_items = order.get("items", [])
        if not order_items:
            return {"success": True, "errors": [], "logs": [], "disabled_menus": []}

        # 2. Collect all unique menuIds from the order
        menu_ids_raw = [item.get("menuId") for item in order_items if item.get("menuId")]

        valid_object_ids = [ObjectId(mid) for mid in menu_ids_raw if ObjectId.is_valid(mid)]
        string_ids = menu_ids_raw

        menu_cursor = db.menus.find({
            "$or": [
                {"_id": {"$in": valid_object_ids}},
                {"menuId": {"$in": string_ids}}
            ]
        })
        all_menus = await menu_cursor.to_list(length=500)

        menus_by_object_id = {str(m["_id"]): m for m in all_menus}
        menus_by_menu_id = {m.get("menuId"): m for m in all_menus if m.get("menuId")}

        def find_menu(menu_id):
            if ObjectId.is_valid(menu_id) and menu_id in menus_by_object_id:
                return menus_by_object_id[menu_id]
            return menus_by_menu_id.get(menu_id)

        # 3. Collect all ingredient names/ids needed across all menus
        ingredient_ids_needed = set()
        ingredient_names_needed = set()
        for item in order_items:
            menu = find_menu(item.get("menuId", ""))
            if not menu:
                continue
            for ing in menu.get("recipe", []):
                if ing.get("ingredientId"):
                    ingredient_ids_needed.add(ing["ingredientId"])
                if ing.get("name"):
                    ingredient_names_needed.add(ing["name"])

        # 4. Fetch all needed inventory items in ONE query
        inventory_cursor = db.inventory.find({
            "$or": [
                {"ingredientId": {"$in": list(ingredient_ids_needed)}},
                {"name": {"$in": list(ingredient_names_needed)}}
            ]
        })
        all_inventory = await inventory_cursor.to_list(length=1000)

        inv_by_ingredient_id = {inv.get("ingredientId"): inv for inv in all_inventory if inv.get("ingredientId")}
        inv_by_name = {inv.get("name"): inv for inv in all_inventory if inv.get("name")}

        def find_inventory(ingredient_id, ingredient_name):
            return inv_by_ingredient_id.get(ingredient_id) or inv_by_name.get(ingredient_name)

        # 5. Process each item and queue stock updates
        update_tasks = []
        log_tasks = []
        now_str = datetime.now().isoformat()

        for item in order_items:
            menu_id = item.get("menuId")
            quantity = item.get("quantity", 1)

            menu = find_menu(menu_id)
            if not menu:
                errors.append(f"Menu {menu_id} not found")
                continue

            recipe = menu.get("recipe", [])
            if not recipe:
                continue

            for ingredient in recipe:
                ingredient_id = ingredient.get("ingredientId")
                ingredient_name = ingredient.get("name")
                ingredient_qty = ingredient.get("quantity", 0) * quantity
                unit = ingredient.get("unit", "unit")

                inventory = find_inventory(ingredient_id, ingredient_name)
                if not inventory:
                    errors.append(f"Ingredient {ingredient_name} not found in inventory")
                    continue

                if inventory["stock"] < ingredient_qty:
                    errors.append(f"Stok {ingredient_name} tidak cukup! Sisa: {inventory['stock']} {inventory['unit']}")
                    continue

                new_stock = inventory["stock"] - ingredient_qty
                inventory["stock"] = new_stock

                update_tasks.append(
                    db.inventory.update_one(
                        {"_id": inventory["_id"]},
                        {"$set": {"stock": new_stock, "updatedAt": now_str}}
                    )
                )

                log = {
                    "orderId": str(order_id),
                    "menuId": menu.get("menuId") or str(menu["_id"]),
                    "menuName": str(menu.get("name")),
                    "ingredientId": inventory.get("ingredientId") or str(inventory["_id"]),
                    "ingredientName": str(inventory.get("name")),
                    "quantity": float(ingredient_qty),
                    "unit": str(unit),
                    "action": "used",
                    "timestamp": now_str,
                    "remainingStock": float(new_stock),
                    "performedBy": "kitchen"
                }
                logs.append(log)
                log_tasks.append(db.stock_logs.insert_one(dict(log)))

        # 6. Run all DB writes concurrently
        if update_tasks or log_tasks:
            await asyncio.gather(*update_tasks, *log_tasks)

        # 🔥 7. DISABLE MENU KALO BAHAN HABIS
        for inv in all_inventory:
            # Ambil stok terbaru dari database (setelah update)
            updated_inv = await db.inventory.find_one({"_id": inv["_id"]})
            if updated_inv and updated_inv.get("stock", 0) <= 0:
                # Cari semua menu yang pake bahan ini
                menus_with_ingredient = await db.menus.find({
                    "$or": [
                        {"recipe.ingredientId": inv.get("ingredientId")},
                        {"recipe.name": inv.get("name")}
                    ]
                }).to_list(length=100)
                
                for menu in menus_with_ingredient:
                    if menu.get("isAvailable") != False:  # Kalo masih aktif
                        await db.menus.update_one(
                            {"_id": menu["_id"]},
                            {"$set": {"isAvailable": False, "updatedAt": datetime.now()}}
                        )
                        disabled_menus.append(menu.get("name"))

        serialized_logs = [serialize_document(log) for log in logs]
        serialized_errors = [str(e) for e in errors]

        return {
            "success": len(errors) == 0,
            "errors": serialized_errors,
            "logs": serialized_logs,
            "disabled_menus": list(set(disabled_menus))  # 🔥 UNIQUE LIST
        }
    except Exception as e:
        print(f"Error in reduce_stock: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))