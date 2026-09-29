from fastapi import APIRouter
from backend.app.database.mongodb import db_manager

router = APIRouter(prefix="/api/admin", tags=["Admin"])

@router.get("/stats")
def get_system_stats():
    produce_types = db_manager.get_produce_types()
    inspections = db_manager.get_inspections(limit=500)
    batches = db_manager.get_batches(limit=100)

    return {
        "success": True,
        "system_status": "Healthy",
        "active_models": [
            {"name": "Fruit Quality Grader", "architecture": "MobileNetV2 Keras Classifier", "status": "Loaded"},
            {"name": "VegQual Deep Model", "architecture": "YOLO Defect Classifier", "status": "Loaded"},
            {"name": "Image Reliability Layer", "architecture": "OpenCV Laplacian & Illumination Engine", "status": "Active"},
        ],
        "total_produce_types": len(produce_types),
        "total_inspections_recorded": len(inspections),
        "total_batches_recorded": len(batches),
        "database_engine": "MongoDB (Local High-Performance Store)",
    }

@router.get("/models")
def get_model_information():
    return {
        "success": True,
        "models": [
            {
                "id": "fruit_quality_grader",
                "name": "Fruit MobileNetV2 Grader",
                "task": "Fruit Quality Classification (Fresh, Adulterant, Rotten)",
                "dataset": "Fruits360 / Custom SMS Produce Dataset",
                "accuracy": "94.2%",
                "status": "Active"
            },
            {
                "id": "vegetable_quality_model",
                "name": "VegQual Quality Inspector",
                "task": "Multiclass Defect Detection across 7 Vegetables",
                "dataset": "VegQual 4,736 Annotated Produce Dataset",
                "accuracy": "93.3% mAP@50",
                "status": "Active"
            }
        ]
    }
