from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime, timedelta
from app.config.database import get_db
from app.utils import serialize_document
import csv
from io import StringIO
from fastapi.responses import StreamingResponse

router = APIRouter(prefix="/stock-stats", tags=["Stock Stats"])

@router.get("/daily-by-category")
async def get_daily_stock_stats_by_category(
    date: str = None,
    db = Depends(get_db)
):
    """
    Get daily stock usage grouped by menu category
    """
    try:
        # TENTUKAN TANGGAL
        if date:
            target_date = datetime.strptime(date, "%Y-%m-%d")
        else:
            target_date = datetime.now()
        
        start_of_day = datetime(target_date.year, target_date.month, target_date.day)
        end_of_day = start_of_day + timedelta(days=1)
        
        # AMBIL LOG STOK
        logs = await db.stock_logs.find({
            "timestamp": {
                "$gte": start_of_day.isoformat(),
                "$lt": end_of_day.isoformat()
            }
        }).to_list(length=1000)
        
        # 🔥 AMBIL DATA MENU UNTUK KATEGORI
        menus = await db.menus.find({}, { "name": 1, "category": 1 }).to_list(length=100)
        menu_category_map = { m["name"]: m.get("category", "Makanan") for m in menus }
        
        # 🔥 GROUP BY KATEGORI + BAHAN
        stats = {}
        for log in logs:
            menu_name = log.get("menuName") or "Unknown"
            category = menu_category_map.get(menu_name, "Makanan")
            ingredient = log.get("ingredientName") or log.get("name")
            qty = log.get("quantity", 0)
            unit = log.get("unit", "unit")
            
            if not ingredient:
                continue
            
            if category not in stats:
                stats[category] = {}
            
            if ingredient not in stats[category]:
                stats[category][ingredient] = {
                    "total": 0,
                    "unit": unit,
                    "menus": []
                }
            
            stats[category][ingredient]["total"] += qty
            if menu_name not in stats[category][ingredient]["menus"]:
                stats[category][ingredient]["menus"].append(menu_name)
        
        # 🔥 FORMAT OUTPUT
        result = []
        for category, ingredients in stats.items():
            ingredient_list = []
            for name, data in ingredients.items():
                ingredient_list.append({
                    "name": name,
                    "total": round(data["total"], 2),
                    "unit": data["unit"],
                    "menus": data["menus"]
                })
            ingredient_list.sort(key=lambda x: x["total"], reverse=True)
            result.append({
                "category": category,
                "ingredients": ingredient_list
            })
        
        # SORT KATEGORI: Makanan, Snack, Minuman
        category_order = ["Makanan", "Snack", "Minuman"]
        result.sort(key=lambda x: category_order.index(x["category"]) if x["category"] in category_order else 99)
        
        return {
            "success": True,
            "date": start_of_day.isoformat(),
            "data": result,
            "total_logs": len(logs)
        }
    except Exception as e:
        print(f"Error in get_daily_stock_stats_by_category: {e}")
        raise HTTPException(status_code=500, detail=str(e))