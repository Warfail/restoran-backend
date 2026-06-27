from bson import ObjectId
from datetime import datetime
from typing import Any, Dict, List, Union

def serialize_document(doc: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convert MongoDB document to JSON serializable format.
    Handles ObjectId and datetime objects.
    """
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

def serialize_value(value: Any) -> Any:
    """Convert a single value to JSON serializable format."""
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

def serialize_list(docs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Convert a list of MongoDB documents to JSON serializable format."""
    return [serialize_document(doc) for doc in docs] if docs else []