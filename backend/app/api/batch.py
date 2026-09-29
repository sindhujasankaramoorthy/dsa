import uuid
import base64
from datetime import datetime
from fastapi import APIRouter, File, UploadFile, Form, HTTPException, Path
from typing import List, Optional
from backend.app.schemas.batch import BatchCreateRequest
from backend.app.services.inference_service import inference_service
from backend.app.services.recommendation_service import recommendation_service
from backend.app.database.mongodb import db_manager

router = APIRouter(prefix="/api/batches", tags=["Batch Inspection"])

@router.post("")
def create_batch(req: BatchCreateRequest):
    batch_id = f"BATCH-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"
    record = {
        "batch_id": batch_id,
        "batch_name": req.batch_name,
        "produce_type": req.produce_type,
        "category": req.category,
        "supplier_name": req.supplier_name,
        "notes": req.notes,
        "created_at": datetime.now().isoformat(),
        "total_inspected": 0,
        "grade_counts": {"A": 0, "B": 0, "C": 0},
        "average_quality_score": 0.0,
        "most_common_defect": "None",
        "recommendation": "Batch initialized. Awaiting image inspections."
    }
    db_manager.insert_batch(record)
    return {"success": True, "batch": record}

@router.get("")
def list_batches():
    batches = db_manager.get_batches(limit=50)
    return {"success": True, "total": len(batches), "batches": batches}

@router.post("/{batch_id}/inspect")
async def inspect_batch_image(
    batch_id: str = Path(...),
    file: Optional[UploadFile] = File(None),
    image_base64: Optional[str] = Form(None),
    produce_hint: Optional[str] = Form(None),
    demo_mode: bool = Form(False)
):
    batch = db_manager.get_batch(batch_id)
    if not batch:
        # Auto-create if requested on demand
        batch = {
            "batch_id": batch_id,
            "batch_name": f"Batch {batch_id}",
            "produce_type": produce_hint or "Tomato",
            "category": "Vegetable",
            "created_at": datetime.now().isoformat()
        }

    image_bytes = None
    if file:
        image_bytes = await file.read()
    elif image_base64:
        if "," in image_base64:
            image_base64 = image_base64.split(",")[1]
        image_bytes = base64.b64decode(image_base64)
    else:
        raise HTTPException(status_code=400, detail="Must provide an image file or base64 payload.")

    hint = produce_hint or batch.get("produce_type")
    result = inference_service.analyze_image(
        image_bytes=image_bytes,
        produce_hint=hint,
        batch_id=batch_id,
        demo_mode=demo_mode
    )

    return {"success": True, "result": result}

@router.get("/{batch_id}")
def get_batch_summary(batch_id: str = Path(...)):
    batch = db_manager.get_batch(batch_id)
    inspections = db_manager.get_inspections({"batch_id": batch_id}, limit=200)

    if not inspections:
        return {
            "success": True,
            "batch_id": batch_id,
            "total_inspected": 0,
            "grade_counts": {"A": 0, "B": 0, "C": 0},
            "grade_percentages": {"A": 0.0, "B": 0.0, "C": 0.0},
            "average_quality_score": 0.0,
            "most_common_defect": "None",
            "defects_breakdown": {},
            "recommendation": "No produce inspections performed for this batch yet.",
            "inspections": []
        }

    total = len(inspections)
    grade_counts = {"A": 0, "B": 0, "C": 0}
    scores = []
    defects_counter = {}

    for ins in inspections:
        grade = ins.get("grade", "B")
        grade_counts[grade] = grade_counts.get(grade, 0) + 1
        scores.append(ins.get("quality_score", 70))
        for d in ins.get("defects", []):
            defects_counter[d] = defects_counter.get(d, 0) + 1

    avg_score = round(sum(scores) / total, 1) if total > 0 else 0.0
    percentages = {k: round((v / total) * 100, 1) for k, v in grade_counts.items()}
    most_common_defect = max(defects_counter, key=defects_counter.get) if defects_counter else "None"
    
    produce_type = inspections[0].get("produce_type", "Produce") if inspections else "Produce"
    rec = recommendation_service.get_batch_recommendation(produce_type, total, grade_counts, avg_score)

    summary = {
        "success": True,
        "batch_id": batch_id,
        "batch_name": batch.get("batch_name", f"Batch {batch_id}") if batch else f"Batch {batch_id}",
        "produce_type": produce_type,
        "category": inspections[0].get("category", "Produce") if inspections else "Produce",
        "created_at": batch.get("created_at", datetime.now().isoformat()) if batch else datetime.now().isoformat(),
        "total_inspected": total,
        "grade_counts": grade_counts,
        "grade_percentages": percentages,
        "average_quality_score": avg_score,
        "most_common_defect": most_common_defect,
        "defects_breakdown": defects_counter,
        "recommendation": rec,
        "inspections": inspections
    }

    return summary
