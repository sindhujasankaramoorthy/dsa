from pydantic import BaseModel
from typing import List, Optional

class ProduceTypeSchema(BaseModel):
    id: str
    name: str
    category: str  # "Fruit" or "Vegetable"
    supported_models: List[str]
    description: Optional[str] = None
    icon: Optional[str] = "🥦"

class ProduceTypeCreate(BaseModel):
    name: str
    category: str
    description: Optional[str] = None
    icon: Optional[str] = "📦"
