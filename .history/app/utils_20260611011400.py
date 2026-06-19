from bson import ObjectId
import json

# Custom JSON encoder buat handle ObjectId
class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        return super().default(obj)

# Fungsi buat convert response
def parse_json(data):
    if data is None:
        return None
    return json.loads(json.dumps(data, cls=CustomJSONEncoder))