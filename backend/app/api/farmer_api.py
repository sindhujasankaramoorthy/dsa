import base64
from fastapi import APIRouter, File, UploadFile, Form, HTTPException, Header
from typing import Optional
from backend.app.services.inference_service import inference_service
from backend.app.services.farmer_decision_service import farmer_decision_service

router = APIRouter(prefix="/api/farmer", tags=["Farmer Decision Assistant"])

@router.post("/analyze-batch")
async def analyze_farmer_harvest_batch(
    file: Optional[UploadFile] = File(None),
    image_base64: Optional[str] = Form(None),
    produce_name: str = Form("Tomato"),
    total_quantity_kg: float = Form(100.0),
    harvest_date: str = Form("Today"),
    location: str = Form("Krishnagiri, Tamil Nadu"),
    buyer_price_per_kg: float = Form(20.0),
    alt_buyer_price_per_kg: Optional[float] = Form(None),
    gemini_api_key: Optional[str] = Form(None),
    x_gemini_api_key: Optional[str] = Header(None, alias="X-Gemini-API-Key")
):
    """
    Farmer Harvest-to-Market Decision Assistant API.
    Analyzes visual quality of harvested batch, estimates Grade A/B/C kg breakdown,
    calculates 3 financial selling scenarios, and outputs practical Next-Step Recommendation.
    """
    image_bytes = None
    if file:
        image_bytes = await file.read()
    elif image_base64:
        if "," in image_base64:
            image_base64 = image_base64.split(",")[1]
        try:
            image_bytes = base64.b64decode(image_base64)
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid base64 image.")

    active_key = gemini_api_key or x_gemini_api_key
    ai_result = None

    if image_bytes:
        ai_result = inference_service.analyze_image(
            image_bytes=image_bytes,
            produce_hint=produce_name,
            gemini_api_key=active_key
        )

    grade = (ai_result or {}).get("grade", "A")
    quality_score = (ai_result or {}).get("quality_score", 82)
    measured_evidence = (ai_result or {}).get("measured_evidence", {})
    defects = (ai_result or {}).get("defects", [])

    farmer_decision = farmer_decision_service.evaluate_farmer_batch(
        produce_name=produce_name,
        total_quantity_kg=total_quantity_kg,
        harvest_date=harvest_date,
        location=location,
        buyer_price_per_kg=buyer_price_per_kg,
        alt_buyer_price_per_kg=alt_buyer_price_per_kg,
        measured_evidence=measured_evidence,
        grade=grade,
        quality_score=quality_score,
        defects=defects
    )

    return {
        "success": True,
        "ai_visual_analysis": ai_result,
        "farmer_decision": farmer_decision
    }
