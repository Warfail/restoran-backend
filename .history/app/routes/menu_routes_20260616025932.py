import uuid
from datetime import datetime

@router.post("/menu")
async def create_menu(menu_data: dict, db = Depends(get_db)):
    # Generate menuId unik
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    random_suffix = str(uuid.uuid4().hex[:4]).upper()
    menu_data["menuId"] = f"MENU{timestamp}{random_suffix}"
    
    result = await db.menus.insert_one(menu_data)
    menu_data["_id"] = str(result.inserted_id)
    
    return {"success": True, "data": menu_data}