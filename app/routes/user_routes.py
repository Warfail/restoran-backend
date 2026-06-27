from fastapi import APIRouter, HTTPException, Depends
from bson import ObjectId
from app.config.database import get_db
import uuid
from datetime import datetime
from serializers import serialize_document, serialize_list, serialize_value

router = APIRouter(prefix="/users", tags=["Users"])

@router.get("/")
async def get_users(db = Depends(get_db)):
    cursor = db.users.find({})
    users = await cursor.to_list(length=100)
    for u in users:
        u["_id"] = str(u["_id"])
    return {"success": True, "data": users}

@router.post("/")
async def create_user(user_data: dict, db = Depends(get_db)):
    username = user_data.get("username")
    if not username:
        raise HTTPException(status_code=400, detail="Username required")
    # Check if exists
    existing = await db.users.find_one({"username": username})
    if existing:
        raise HTTPException(status_code=400, detail="Username already exists")
    
    new_user = {
        "userId": str(uuid.uuid4())[:8],
        "username": username,
        "password": user_data.get("password"),
        "fullName": user_data.get("name"),
        "email": user_data.get("email"),
        "phone": user_data.get("phone"),
        "role": user_data.get("role"),
        "isActive": user_data.get("isActive", True),
        "branch": user_data.get("branch", "salatiga"),
        "createdAt": datetime.now().isoformat()
    }
    result = await db.users.insert_one(new_user)
    new_user["_id"] = str(result.inserted_id)
    return {"success": True, "data": new_user}

@router.put("/{user_id}")
async def update_user(user_id: str, data: dict, db = Depends(get_db)):
    result = await db.users.update_one({"_id": ObjectId(user_id)}, {"$set": data})
    return {"success": True}

@router.delete("/{user_id}")
async def delete_user(user_id: str, db = Depends(get_db)):
    await db.users.delete_one({"_id": ObjectId(user_id)})
    return {"success": True}
