from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from app.config.database import get_db
import os
import uuid
from datetime import datetime

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

import uuid
from datetime import datetime

def process_forgot_password_email(email: str, reset_link: str):
    from app.utils.email_service import send_reset_email
    email_sent = send_reset_email(email, reset_link)
    
    if not email_sent:
        print("=" * 50)
        print(f"⚠️ SIMULASI EMAIL TERKIRIM KE: {email}")
        print(f"🔗 LINK RESET: {reset_link}")
        print("=" * 50)

@router.post("/forgot-password")
async def forgot_password(data: dict, db = Depends(get_db)):
    email = data.get("email")
    if not email:
        raise HTTPException(status_code=400, detail="Email wajib diisi")
    
    user = await db.users.find_one({"email": email})
    if not user:
        raise HTTPException(status_code=404, detail="Email tidak terdaftar")
    
    # Generate token
    reset_token = str(uuid.uuid4())
    await db.users.update_one(
        {"_id": user["_id"]},
        {"$set": {
            "resetToken": reset_token,
            "resetTokenExp": datetime.now().timestamp() + 3600
        }}
    )
    
    # 🔥 KIRIM VIA EMAIL (di background sepenuhnya)
    frontend_url = os.getenv("FRONTEND_URL", "http://localhost:5173")
    reset_link = f"{frontend_url}/reset-password?token={reset_token}"
    
    import asyncio
    from fastapi.concurrency import run_in_threadpool
    asyncio.create_task(run_in_threadpool(process_forgot_password_email, email, reset_link))
    
    return {"success": True, "message": "Tautan reset telah dikirim ke email Anda."}
@router.post("/reset-password")
async def reset_password(data: dict, db = Depends(get_db)):
    token = data.get("token")
    new_password = data.get("password")
    
    if not token or not new_password:
        raise HTTPException(status_code=400, detail="Token dan kata sandi baru wajib diisi")
        
    # Cari user dengan token yang valid
    user = await db.users.find_one({"resetToken": token})
    
    if not user:
        raise HTTPException(status_code=400, detail="Token tidak valid atau sudah kedaluwarsa")
        
    # Validasi expiry (1 jam)
    exp = user.get("resetTokenExp", 0)
    if datetime.now().timestamp() > exp:
        raise HTTPException(status_code=400, detail="Token sudah kedaluwarsa")
        
    # Update password dan hapus token
    await db.users.update_one(
        {"_id": user["_id"]},
        {
            "$set": {"password": new_password},
            "$unset": {"resetToken": "", "resetTokenExp": ""}
        }
    )
    
    return {"success": True, "message": "Kata sandi berhasil diatur ulang"}


