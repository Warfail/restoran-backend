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
    if data is None:
        return None
    return json.loads(json.dumps(data, cls=CustomJSONEncoder))