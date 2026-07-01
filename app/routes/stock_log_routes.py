from fastapi import APIRouter, Depends
from app.config.database import get_db

router = APIRouter(prefix="/stock-logs", tags=["Stock Logs"])

@router.get("/")
async def get_stock_logs(db = Depends(get_db)):
    cursor = db.stock_logs.find({}).sort("timestamp", -1).limit(50)
    logs = await cursor.to_list(length=50)
    for log in logs:
        log["_id"] = str(log["_id"])
    return {"success": True, "data": logs}