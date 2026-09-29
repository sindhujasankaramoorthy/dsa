import os
import cv2
import numpy as np
import base64
import uuid
from datetime import datetime
from typing import Dict, Any, Tuple, Optional

from backend.app.services.image_quality_service import image_quality_service
from backend.app.services.fruit_service import fruit_service
from backend.app.services.vegetable_service import vegetable_service
from backend.app.services.grading_service import grading_service
from backend.app.services.recommendation_service import recommendation_service
from backend.app.services.gemini_service import gemini_service
from backend.app.database.mongodb import db_manager

VEGETABLES_LIST = {"tomato", "potato", "bitter gourd", "pointed gourd", "onion", "capsicum", "brinjal"}
FRUITS_LIST = {"apple", "banana", "pomegranate", "orange", "mango"}

GRADING_DISCLAIMER = (
    "Operational Grade A/B/C is a facility sorting mapping derived from source model defect classifications "
    "and measured surface vision metrics (rot ratio, discoloration, texture density). It is not a USDA certified laboratory grade."
)

class InferenceService:
    """Central Produce Inference Service orchestrating Image Quality, Gemini AI Vision, Produce Detection, Model Routing, Evidence Extraction & Recommendations."""

    def analyze_image(
        self,
        image_bytes: bytes,
        produce_hint: Optional[str] = None,
        batch_id: Optional[str] = None,
        user_id: Optional[str] = "user_default",
        demo_mode: bool = False,
        gemini_api_key: Optional[str] = None
    ) -> Dict[str, Any]:
        
        # 1. Decode Image
        nparr = np.frombuffer(image_bytes, np.uint8)
        image_np = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if image_np is None:
            return {
                "error": "Failed to decode produce image. Please provide a valid JPG or PNG file.",
                "image_quality_passed": False
            }

        # 2. Image Reliability Layer (Pre-inspection Quality Check)
        passed, quality_msg, quality_details = image_quality_service.validate_image(image_np)

        if not passed and not demo_mode:
            return {
                "error": quality_msg,
                "image_quality_passed": False,
                "image_quality_details": quality_details
            }

        # 3. Check for Gemini API key override / environment configuration
        active_gemini_key = gemini_api_key or os.getenv("GEMINI_API_KEY")
        if active_gemini_key and gemini_service.is_configured(active_gemini_key):
            try:
                gemini_res = gemini_service.analyze_with_gemini(
                    image_bytes=image_bytes,
                    api_key=active_gemini_key,
                    produce_hint=produce_hint
                )
                if gemini_res:
                    inspection_id = f"INS-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"
                    timestamp_str = datetime.now().isoformat()
                    
                    response_dict = {
                        "inspection_id": inspection_id,
                        "batch_id": batch_id,
                        "produce_type": gemini_res.get("produce_type", produce_hint or "Produce").title(),
                        "category": gemini_res.get("category", "Fruit"),
                        "raw_model_prediction": gemini_res.get("quality", "Fresh"),
                        "quality": gemini_res.get("quality", "Fresh"),
                        "grade": gemini_res.get("grade", "A"),
                        "quality_score": gemini_res.get("quality_score", 85),
                        "confidence": gemini_res.get("confidence", 0.95),
                        "measured_evidence": gemini_res.get("measured_evidence", {}),
                        "visible_factors": gemini_res.get("visible_factors", {}),
                        "defects": gemini_res.get("defects", []),
                        "evidence_reasoning": gemini_res.get("evidence_reasoning", "Evaluated via Gemini Multimodal Vision AI."),
                        "recommendation": gemini_res.get("recommendation", {}),
                        "model_used": gemini_res.get("model_used", "Gemini Multimodal AI"),
                        "grading_disclaimer": GRADING_DISCLAIMER,
                        "image_quality_passed": True,
                        "image_quality_details": quality_details,
                        "image_url": None,
                        "timestamp": timestamp_str,
                        "is_demo": demo_mode
                    }

                    # Persist record
                    db_record = dict(response_dict)
                    db_record["user_id"] = user_id
                    db_manager.insert_inspection(db_record)
                    return response_dict
            except Exception as g_err:
                logger.warning(f"Gemini API inspection error: {g_err}. Falling back to local CV pipeline.")

        # 4. Local Produce Detection & Category Routing Fallback
        produce_type, category = self.detect_produce_type_and_category(image_np, produce_hint)

        # 4. Select Model & Predict Quality + Extract Measured Evidence
        if category == "Fruit":
            raw_condition, confidence, model_used, evidence_dict = fruit_service.predict_quality(image_np, produce_type)
        else:
            raw_condition, confidence, model_used, evidence_dict = vegetable_service.predict_quality(image_np, produce_type)

        # Handle Demo Mode Adjustments
        if demo_mode and produce_hint:
            if "rotten" in produce_hint.lower() or "defective" in produce_hint.lower():
                raw_condition = "Rotten" if category == "Fruit" else "Defective"
                confidence = 0.94
                evidence_dict["rot_ratio_pct"] = 14.5
            elif "fresh" in produce_hint.lower():
                raw_condition = "Fresh"
                confidence = 0.96
                evidence_dict["rot_ratio_pct"] = 0.5

        # 5. Standardized Grade Mapping & Evidence-Based Reasoning
        (
            grade,
            quality_label,
            quality_score,
            conf_val,
            measured_evidence,
            visible_factors,
            defects,
            reasoning
        ) = grading_service.compute_grade_and_score(raw_condition, confidence, image_np, evidence_dict)

        # 6. Business Recommendation
        recommendation = recommendation_service.get_single_recommendation(produce_type, grade, quality_score)

        # Construct Unified Evidence-Grounded Response
        inspection_id = f"INS-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"
        timestamp_str = datetime.now().isoformat()

        response_dict = {
            "inspection_id": inspection_id,
            "batch_id": batch_id,
            "produce_type": produce_type.title(),
            "category": category,
            "raw_model_prediction": raw_condition,
            "quality": quality_label,
            "grade": grade,
            "quality_score": quality_score,
            "confidence": conf_val,
            "measured_evidence": measured_evidence.model_dump(),
            "visible_factors": visible_factors.model_dump(),
            "defects": defects,
            "evidence_reasoning": reasoning,
            "recommendation": recommendation,
            "model_used": model_used,
            "grading_disclaimer": GRADING_DISCLAIMER,
            "image_quality_passed": True,
            "image_quality_details": quality_details,
            "image_url": None,
            "timestamp": timestamp_str,
            "is_demo": demo_mode
        }

        # Persist to database
        db_record = dict(response_dict)
        db_record["user_id"] = user_id
        db_manager.insert_inspection(db_record)

        return response_dict

    def detect_produce_type_and_category(
        self, image_np: np.ndarray, hint: Optional[str] = None
    ) -> Tuple[str, str]:
        if hint and hint.strip():
            hint_clean = hint.strip().lower()
            if hint_clean in VEGETABLES_LIST or any(v in hint_clean for v in VEGETABLES_LIST):
                return hint_clean.title(), "Vegetable"
            if hint_clean in FRUITS_LIST or any(f in hint_clean for f in FRUITS_LIST):
                return hint_clean.title(), "Fruit"
            return hint_clean.title(), "Vegetable"

        # Image color centroid heuristic for category estimation if hint is absent
        hsv = cv2.cvtColor(image_np, cv2.COLOR_BGR2HSV)
        avg_hue = np.mean(hsv[:, :, 0])
        
        if 35 < avg_hue < 85: # Green range -> Vegetable (Capsicum/Bitter Gourd)
            return "Capsicum", "Vegetable"
        elif avg_hue < 20 or avg_hue > 160: # Red range -> Tomato
            return "Tomato", "Vegetable"
        else:
            return "Banana", "Fruit"

inference_service = InferenceService()
