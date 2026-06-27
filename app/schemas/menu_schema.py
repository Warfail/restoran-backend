from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List, Dict, Any

class MenuCreate(BaseModel):
    name: str
    category: str
    price: int          # ← integer
    stock: int          # ← integer
    description: Optional[str] = ""
    isAvailable: bool = True
    image: Optional[str] = "https://placehold.co/100x80/c8a96e/c8a96e"
    ingredients: Optional[List[Dict[str, Any]]] = []