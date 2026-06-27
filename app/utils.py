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