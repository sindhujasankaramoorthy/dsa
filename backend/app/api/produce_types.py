import uuid
from fastapi import APIRouter
from backend.app.schemas.produce import ProduceTypeCreate
from backend.app.database.mongodb import db_manager

router = APIRouter(prefix="/api/produce-types", tags=["Produce Types"])

@router.get("")
def list_produce_types():
    types = db_manager.get_produce_types()
    return {"success": True, "total": len(types), "produce_types": types}

@router.post("")
def add_produce_type(req: ProduceTypeCreate):
    pid = req.name.lower().replace(" ", "_")
    item = {
        "id": pid,
        "name": req.name,
        "category": req.category,
        "supported_models": ["vegetable_quality_model" if req.category == "Vegetable" else "fruit_quality_grader"],
        "description": req.description,
        "icon": req.icon or "📦"
    }
    db_manager.insert_produce_type(item)
    return {"success": True, "produce_type": item}
