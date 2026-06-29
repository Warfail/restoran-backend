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
    elif isinstance(value, datetime