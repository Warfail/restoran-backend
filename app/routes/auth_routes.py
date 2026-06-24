from fastapi import APIRouter, HTTPException, Depends
from app.config.database import get_db

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/login")
async def login(credentials: dict, db = Depends(get_db)):
    username = credentials.get("username")
    password = credentials.get("password")
    
    user = await db.users.find_one({"username": username, "password": password})
    if not user:
        raise HTTPException(status_code=401, detail="Username atau password salah")
    
    if not user.get("isActive", True):
        raise HTTPException(status_code=403, detail="Akun anda dinonaktifkan")
    
    return {
        "success": True,
        "token": "real-token-123",
        "role": user["role"],
        "user": {
            "userId": str(user["_id"]),
            "username": user["username"],
            "fullName": user.get("fullName", user["username"]),
            "role": user["role"],
            "profilePicture": user.get("profilePicture", "")
        }
    }
