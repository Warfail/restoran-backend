from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime, timedelta
from app.config.database import get_db
from app.utils import serialize_document
import csv
from io import StringIO
from fastapi.responses import StreamingResponse

router = APIRouter(prefix="/stock-stats", tags=["Stock Stats"])

@router.get("/daily")
async def get_daily_stock_stats(
    date: str = None,
    db = Depends(get_db)
):
    """
    Get stock usage statistics per day
    - date: YYYY-MM-DD (default: today)
    """
    try:
        # TENTUKAN TANGGAL
        if date:
            try:
                target_date = datetime.strptime(date, "%Y-%m-%d")
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
        else:
            target_date = datetime.now()
        
        # RENTANG WAKTU
        start_of_day = datetime(target_date.year, target_date.month, target_date.day)
        end_of_day = start_of_day + timedelta(days=1)
        
        # AMBIL LOG STOK HARI INI
        logs = await db.stock_logs.find({
            "timestamp": {
                "$gte": start_of_day.isoformat(),
                "$lt": end_of_day.isoformat()
            }
        }).to_list(length=1000)
        
        # GROUP BY BAHAN
        stats = {}
        for log in logs:
            name = log.get("ingredientName") or log.get("name")
            qty = log.get("quantity", 0)
            unit = log.get("unit", "unit")
            menu_name = log.get("menuName") or "Unknown"
            
            if not name:
                continue
                
            if name not in stats:
                stats[name] = {
                    "total": 0,
                    "unit": unit,
                    "menus": []
                }
            
            stats[name]["total"] += qty
            if menu_name not in stats[name]["menus"]:
                stats[name]["menus"].append(menu_name)
        
        # FORMAT OUTPUT
        result = []
        for name, data in stats.items():
            result.append({
                "name": name,
                "total": round(data["total"], 2),
                "unit": data["unit"],
                "menus": data["menus"]
            })
        
        result.sort(key=lambda x: x["total"], reverse=True)
        
        return {
            "success": True,
            "date": start_of_day.isoformat(),
            "data": result,
            "total_logs": len(logs)
        }
    except Exception as e:
        print(f"Error in get_daily_stock_stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/weekly")
async def get_weekly_stock_stats(
    db = Depends(get_db)
):
    """
    Get stock usage statistics for the last 7 days
    """
    try:
        today = datetime.now()
        start_date = today - timedelta(days=7)
        start_of_day = datetime(start_date.year, start_date.month, start_date.day)
        
        logs = await db.stock_logs.find({
            "timestamp": {
                "$gte": start_of_day.isoformat()
            }
        }).to_list(length=2000)
        
        stats = {}
        for log in logs:
            name = log.get("ingredientName") or log.get("name")
            qty = log.get("quantity", 0)
            unit = log.get("unit", "unit")
            
            if not name:
                continue
                
            if name not in stats:
                stats[name] = {
                    "total": 0,
                    "unit": unit
                }
            
            stats[name]["total"] += qty
        
        result = []
        for name, data in stats.items():
            result.append({
                "name": name,
                "total": round(data["total"], 2),
                "unit": data["unit"]
            })
        
        result.sort(key=lambda x: x["total"], reverse=True)
        
        return {
            "success": True,
            "period": "7_days",
            "start_date": start_of_day.isoformat(),
            "data": result,
            "total_logs": len(logs)
        }
    except Exception as e:
        print(f"Error in get_weekly_stock_stats: {e}")
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
        stats_response = await get_daily_stock_stats(date, db)
        if not stats_response.get("success"):
            raise HTTPException(status_code=500, detail="Failed to get stats")
        
        data = stats_response.get("data", [])
        date_str = stats_response.get("date", datetime.now().isoformat())
        
        # BUAT CSV
        output = StringIO()
        writer = csv.writer(output)
        
        # HEADER
        writer.writerow(["Bahan", "Total Terpakai", "Unit", "Menu Terkait"])
        
        # DATA
        for item in data:
            writer.writerow([
                item["name"],
                item["total"],
                item["unit"],
                ", ".join(item["menus"])
            ])
        
        # FOOTER
        writer.writerow([])
        writer.writerow(["Total Log", len(data)])
        
        # RETURN CSV
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