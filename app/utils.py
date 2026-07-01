from bson import ObjectId
import json
from datetime import datetime
from app.utils.serializers import serialize_document, serialize_list, serialize_value

class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        if isinstance(obj, datetime):
            return obj.isoformat()  # Convert datetime ke string ISO format
        return super().default(obj)
    
    
    # app/utils.py

def format_stock(value):
    """Format angka stok ke 2 desimal"""
    if value is None:
        return "0"
    return f"{round(value, 2):.2f}".rstrip('0').rstrip('.')

def convert_to_small_unit(stock, unit):
    """Konversi stok dari besar ke kecil"""
    conversions = {
        "kg": {"multiplier": 1000, "small_unit": "gr"},
        "liter": {"multiplier": 1000, "small_unit": "ml"},
        "dus": {"multiplier": 24, "small_unit": "pcs"},
        "karung": {"multiplier": 50, "small_unit": "kg"},
        "ons": {"multiplier": 100, "small_unit": "gr"},
    }
    if unit in conversions:
        return {
            "value": stock * conversions[unit]["multiplier"],
            "unit": conversions[unit]["small_unit"]
        }
    return {"value": stock, "unit": unit}


def parse_json(data):
    """
    Convert MongoDB document to JSON serializable format.
    """
    if not data:
        return data
    from bson import ObjectId
    from datetime import datetime
    
    if isinstance(data, list):
        return [parse_json(item) for item in data]
    elif isinstance(data, dict):
        result = {}
        for key, value in data.items():
            if isinstance(value, ObjectId):
                result[key] = str(value)
            elif isinstance(value, datetime):
                result[key] = value.isoformat()
            elif isinstance(value, list):
                result[key] = [parse_json(item) for item in value]
            elif isinstance(value, dict):
                result[key] = parse_json(value)
            else:
                result[key] = value
        return result
    else:
        return data