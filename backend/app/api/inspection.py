import base64
from fastapi import APIRouter, File, UploadFile, Form, HTTPException, Query, Header
from typing import Optional, List
from backend.app.services.inference_service import inference_service
from backend.app.database.mongodb import db_manager

router = APIRouter(prefix="/api", tags=["Inspection"])

@router.post("/inspect")
async def inspect_produce(
    file: Optional[UploadFile] = File(None),
    image_base64: Optional[str] = Form(None),
    produce_hint: Optional[str] = Form(None),
    batch_id: Optional[str] = Form(None),
    demo_mode: bool = Form(False),
    gemini_api_key: Optional[str] = Form(None),
    x_gemini_api_key: Optional[str] = Header(None, alias="X-Gemini-API-Key")
):
    """
    Main Produce Inspection API Endpoint.
    Accepts multipart file upload or Base64 encoded produce image string,
    with optional Gemini API Key override for multimodal AI inspection.
    """
    active_key = gemini_api_key or x_gemini_api_key
    image_bytes = None

    if file:
        image_bytes = await file.read()
    elif image_base64:
        # Strip data URL header if present
        if "," in image_base64:
            image_base64 = image_base64.split(",")[1]
        try:
            image_bytes = base64.b64decode(image_base64)
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid Base64 image payload.")
    else:
        raise HTTPException(status_code=400, detail="Must provide an image file or base64 string.")

    result = inference_service.analyze_image(
        image_bytes=image_bytes,
        produce_hint=produce_hint,
        batch_id=batch_id,
        demo_mode=demo_mode,
        gemini_api_key=active_key
    )

    if "error" in result and not result.get("image_quality_passed", True):
        return {
            "success": False,
            "message": result["error"],
            "image_quality_passed": False,
            "image_quality_details": result.get("image_quality_details", {})
        }

    return {"success": True, "result": result}

@router.get("/inspections")
def get_inspection_history(limit: int = Query(50, ge=1, le=200)):
    """Fetch recent produce inspection records."""
    records = db_manager.get_inspections(limit=limit)
    return {"success": True, "total": len(records), "inspections": records}
