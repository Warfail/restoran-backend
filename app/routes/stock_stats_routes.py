from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime, timedelta
from app.config.database import get_db
from app.utils import serialize_document
import csv
from io import StringIO
from fastapi.responses import StreamingResponse

router = APIRouter(prefix="/stock-stats", tags=["Stock Stats"])

@router.get("/daily-flat")
async def get_daily_stock_stats_flat(
    date: str = None,
    db = Depends(get_db)
):
    """
    Get daily stock usage as flat list (not grouped by category)
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
        
        # AMBIL DATA MENU UNTUK KATEGORI
        menus = await db.menus.find({}, { "name": 1, "category": 1 }).to_list(length=100)
        menu_category_map = { m["name"]: m.get("category", "Makanan") for m in menus }
        
        # GROUP BY BAHAN (FLAT)
        stats = {}
        for log in logs:
            menu_name = log.get("menuName") or "Unknown"
            category = menu_category_map.get(menu_name, "Makanan")
            ingredient = log.get("ingredientName") or log.get("name")
            qty = log.get("quantity", 0)
            unit = log.get("unit", "unit")
            
            if not ingredient:
                continue
            
            if ingredient not in stats:
                stats[ingredient] = {
                    "name": ingredient,
                    "total": 0,
                    "unit": unit,
                    "category": category,
                    "menus": []
                }
            
            stats[ingredient]["total"] += qty
            if menu_name not in stats[ingredient]["menus"]:
                stats[ingredient]["menus"].append(menu_name)
        
        # FORMAT OUTPUT
        result = list(stats.values())
        for item in result:
            item["total"] = round(item["total"], 2)
        
        result.sort(key=lambda x: x["total"], reverse=True)
        
        return {
            "success": True,
            "date": start_of_day.isoformat(),
            "data": result,
            "total_logs": len(logs)
        }
    except Exception as e:
        print(f"Error in get_daily_stock_stats_flat: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/export/daily-csv")
async def export_daily_csv(
    date: str = None,
    db = Depends(get_db)
):
    """
    Export daily stock usage as CSV
    """
    try:
        # DAPATKAN DATA
        stats_response = await get_daily_stock_stats_flat(date, db)
        if not stats_response.get("success"):
            raise HTTPException(status_code=500, detail="Failed to get stats")
        
        data = stats_response.get("data", [])
        date_str = stats_response.get("date", datetime.now().isoformat())
        
        # BUAT CSV
        output = StringIO()
        writer = csv.writer(output)
        
        # HEADER
        writer.writerow(["Bahan", "Total Terpakai", "Unit", "Kategori", "Menu Terkait"])
        
        # DATA
        for item in data:
            writer.writerow([
                item["name"],
                item["total"],
                item["unit"],
                item["category"],
                ", ".join(item["menus"])
            ])
        
        # FOOTER
        writer.writerow([])
        writer.writerow(["Total Bahan Terpakai", len(data)])
        
        return StreamingResponse(
            iter([output.getvalue()]),
            media_type="text/csv",
            headers={
                "Content-Disposition": f"attachment; filename=stock-usage-{date_str[:10]}.csv"
            }
        )
    except Exception as e:
        print(f"Error in export_daily_csv: {e}")
        raise HTTPException(status_code=500, detail=str(e))