from fastapi import APIRouter, Query, Form, Body
from typing import Optional, List, Dict, Any
from backend.app.services.industry_guide_service import industry_guide_service

router = APIRouter(prefix="/api/industry-guide", tags=["Grade-to-Industry Guide"])

@router.post("/evaluate")
def evaluate_grade_to_industry(
    produce_name: str = Body("Tomato"),
    grade: str = Body("B"),
    quality_score: int = Body(80),
    defects: List[str] = Body([]),
    measured_evidence: Dict[str, Any] = Body({}),
    grade_a_kg: Optional[float] = Body(None),
    grade_b_kg: Optional[float] = Body(None),
    grade_c_kg: Optional[float] = Body(None)
):
    """
    Evaluates existing AI Grade & visual defects to recommend selling destinations,
    processing industry suggestions, batch split guidance, and local demo buyers.
    """
    destination_eval = industry_guide_service.evaluate_destination(
        produce_name=produce_name,
        grade=grade,
        defects=defects,
        measured_evidence=measured_evidence,
        quality_score=quality_score
    )

    batch_eval = None
    if grade_a_kg is not None and grade_b_kg is not None and grade_c_kg is not None:
        batch_eval = industry_guide_service.evaluate_batch_destinations(
            produce_name=produce_name,
            grade_a_kg=grade_a_kg,
            grade_b_kg=grade_b_kg,
            grade_c_kg=grade_c_kg,
            grade_c_severe=destination_eval.get("is_severe_rot", False)
        )

    buyers = industry_guide_service.get_buyers(
        produce_name=produce_name,
        grade_filter=grade,
        category_filter=destination_eval.get("destination_category")
    )

    return {
        "success": True,
        "destination_guide": destination_eval,
        "batch_guidance": batch_eval,
        "buyer_records": buyers,
        "disclaimer_note": "Demo buyer records provided. Recommendations are visual quality assessment only."
    }

@router.get("/buyers")
def get_industry_buyers(
    produce_name: Optional[str] = Query(None),
    grade: Optional[str] = Query(None),
    category: Optional[str] = Query(None)
):
    """Fetch demo buyers and industry contacts."""
    buyers = industry_guide_service.get_buyers(
        produce_name=produce_name,
        grade_filter=grade,
        category_filter=category
    )
    return {
        "success": True,
        "total": len(buyers),
        "buyers": buyers,
        "disclaimer": industry_guide_service.evaluate_destination("Tomato", "B")["safety_disclaimer_en"]
    }

@router.get("/suggestions")
def get_processing_suggestions(
    produce_name: str = Query("Tomato"),
    grade: str = Query("B")
):
    """Fetch configurable processing industry suggestions."""
    suggestions = industry_guide_service.get_processing_suggestions(produce_name, grade)
    return {
        "success": True,
        "produce_name": produce_name,
        "suggestions": suggestions
    }
