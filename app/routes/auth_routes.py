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

import uuid
from datetime import datetime

@router.post("/forgot-password")
async def forgot_password(data: dict, db = Depends(get_db)):
    email = data.get("email")
    if not email:
        raise HTTPException(status_code=400, detail="Email wajib diisi")
    
    # Cari user berdasarkan email
    user = await db.users.find_one({"email": email})
    if not user:
        raise HTTPException(status_code=400, detail="Email tidak terdaftar")
        
    # Generate token
    reset_token = str(uuid.uuid4())
    
    # Simpan token ke db user
    await db.users.update_one(
        {"_id": user["_id"]},
        {"$set": {"resetToken": reset_token, "resetTokenExp": datetime.now().timestamp() + 3600}} # Berlaku 1 jam
    )
    
    from app.utils.email_service import send_reset_email
    
    # Kirim email (jika SMTP diatur) atau sekadar print di terminal
    reset_link = f"http://localhost:5173/reset-password?token={reset_token}"
    email_sent = send_reset_email(email, reset_link)
    
    if not email_sent:
        print("=" * 50)
        print(f"SIMULASI EMAIL TERKIRIM KE: {email}")
        print(f"LINK RESET PASSWORD: {reset_link}")
        print("=" * 50)
    
    return {"success": True, "message": "Tautan reset kata sandi telah dikirim ke email Anda."}

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
