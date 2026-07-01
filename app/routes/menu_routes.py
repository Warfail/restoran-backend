from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime
from bson import ObjectId
from app.config.database import get_db
from app.utils import parse_json

router = APIRouter(prefix="/menu", tags=["Menu"])

@router.get("/")
async def get_all_menus(
    page: int = 1, 
    limit: int = 10,
    db = Depends(get_db)
):
    try:
        # Validasi parameter
        if page < 1:
            page = 1
        if limit < 1 or limit > 50:
            limit = 10

        skip = (page - 1) * limit
        cursor = db.menus.find({}).skip(skip).limit(limit)
        menus = await cursor.to_list(length=limit)
        total = await db.menus.count_documents({})
        
        # 🔥 PAKE PARSE_JSON BUAT SERIALIZE
        return {
            "success": True,
            "data": parse_json(menus),
            "pagination": {
                "page": page,
                "limit": limit,
                "total": total,
                "totalPages": (total + limit - 1) // limit if total > 0 else 1
            }
        }
    except Exception as e:
        print(f"Error in get_all_menus: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")