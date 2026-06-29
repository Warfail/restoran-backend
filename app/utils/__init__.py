from bson import ObjectId
import json
from datetime import datetime

def serialize_document(doc):
    if not doc:
        return {}
    result = {}
    for key, value in doc.items():
        if isinstance(value, ObjectId):
            result[key] = str(value)
        elif isinstance(value, datetime):
            result[key] = value.isoformat()
        elif isinstance(value, list):
            result[key] = [serialize_value(item) for item in value]
        elif isinstance(value, dict):
            result[key] = serialize_document(value)
        else:
            result[key] = value
    return result

def serialize_value(value):
    if isinstance(value, ObjectId):
        return str(value)
    elif isinstance(value, datetime):
        return value.isoformat()
    elif isinstance(value, list):
        return [serialize_value(item) for item in value]
    elif isinstance(value, dict):
        return serialize_document(value)
    else:
        return value

def serialize_list(docs):
    return [serialize_document(doc) for doc in docs] if docs else []

class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)

def parse_json(data):
    if data is None:
        return None
    return json.loads(json.dumps(data, cls=CustomJSONEncoder))