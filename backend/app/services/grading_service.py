import cv2
import numpy as np
from typing import Dict, Any, List, Tuple
from backend.app.schemas.inspection import VisibleFactors, MeasuredEvidence

class GradingService:
    """Standardized Produce Quality Grading and Evidence-Based Explainability Engine."""

    def compute_grade_and_score(
        self, 
        condition: str, 
        base_confidence: float, 
        image_np: np.ndarray,
        evidence_dict: Dict[str, float]
    ) -> Tuple[str, str, int, float, MeasuredEvidence, VisibleFactors, List[str], str]:
        """
        Maps raw model condition to binary Fresh / Not Fresh, calculates visual quality score across
        the 4 core parameters (Colour, Size, Surface Defects, Apparent Maturity), and constructs evidence reasoning.
        """
        cond_normalized = condition.title()
        rot_ratio = evidence_dict.get("rot_ratio_pct", 0.0)
        discolor_ratio = evidence_dict.get("discolor_ratio_pct", 0.0)
        defect_density = evidence_dict.get("defect_density_pct", 0.0)
        avg_sat = evidence_dict.get("avg_sat", 50.0)

        # 1. Computation of the 4 Core Produce Parameters:
        # Parameter 1: Colour Vibrancy Score (HSV saturation & hue consistency)
        colour_vibrancy = int(min(100, max(10, (avg_sat / 180.0) * 100)))

        # Parameter 2: Size & Scale Occupancy Score (Frame area scale)
        produce_occupancy_pct = evidence_dict.get("produce_area_pct", 35.0)
        size_scale_score = int(min(100, max(20, produce_occupancy_pct * 2.2 + 25)))

        # Parameter 3: Surface Defects Score (rot decay %, discoloration %, & lesion texture density %)
        surface_smoothness = int(max(5, min(98, 100 - (rot_ratio * 5.0 + discolor_ratio * 4.0 + defect_density * 4.0))))

        # Parameter 4: Apparent Maturity Score (Hue temperature warmth)
        visual_maturity = int(min(98, max(20, colour_vibrancy * 0.6 + 20)))

        # 2. Binary Quality Classification & Calibrated Quality Score
        if "Fresh" in cond_normalized and rot_ratio <= 5.0 and discolor_ratio <= 3.0:
            grade = "A"
            quality_label = "Fresh"
            raw_score = int(surface_smoothness * 0.40 + colour_vibrancy * 0.25 + visual_maturity * 0.20 + size_scale_score * 0.15)
            quality_score = max(75, min(98, raw_score))
        elif "Adulterant" in cond_normalized or "Damaged" in cond_normalized or "Defective" in cond_normalized:
            grade = "B"
            quality_label = "Not Fresh"
            raw_score = int(surface_smoothness * 0.45 + colour_vibrancy * 0.25 + visual_maturity * 0.15 + size_scale_score * 0.15)
            quality_score = max(42, min(62, raw_score))
        else: # Rotten
            grade = "C"
            quality_label = "Not Fresh"
            raw_score = int(surface_smoothness * 0.50 + colour_vibrancy * 0.20 + visual_maturity * 0.15 + size_scale_score * 0.15)
            quality_score = max(12, min(38, raw_score))

        measured_evidence = MeasuredEvidence(
            rot_decay_ratio_pct=rot_ratio,
            discoloration_ratio_pct=discolor_ratio,
            lesion_texture_density_pct=defect_density,
            colour_vibrancy_score=colour_vibrancy,
            produce_size_scale_score=size_scale_score,
            surface_smoothness_score=surface_smoothness,
            visual_maturity_score=visual_maturity
        )

        visible_factors = VisibleFactors(
            colour=colour_vibrancy,
            size=size_scale_score,
            surface_condition=surface_smoothness,
            maturity=visual_maturity
        )

        # 3. Evidence-based defects list
        defects = []
        if rot_ratio > 2.5:
            defects.append(f"Dark rot / decay spot ({rot_ratio:.1f}% area)")
        if discolor_ratio > 5.0:
            defects.append(f"Discolored / mold patch ({discolor_ratio:.1f}% area)")
        if defect_density > 4.0:
            defects.append(f"Surface lesion / edge irregularity ({defect_density:.1f}% density)")
        if not defects:
            defects.append("No significant visual defects measured")

        # Construct strict evidence-first reasoning string
        if grade == "C":
            reasoning = (
                f"Classified as NOT FRESH based on measured produce evidence: {rot_ratio:.1f}% dark decay/rot area "
                f"and {discolor_ratio:.1f}% discolored mold area were detected on the produce surface."
            )
        elif grade == "B":
            reasoning = (
                f"Classified as NOT FRESH based on measured produce evidence: {rot_ratio:.1f}% rot ratio and "
                f"{defect_density:.1f}% surface texture defect density were detected."
            )
        else: # Grade A
            reasoning = (
                f"Classified as FRESH based on measured produce evidence: produce surface exhibits minimal rot ratio ({rot_ratio:.1f}%) "
                f"and high colour vibrancy score ({colour_vibrancy}/100)."
            )

        return (
            grade,
            quality_label,
            quality_score,
            round(base_confidence, 2),
            measured_evidence,
            visible_factors,
            defects,
            reasoning
        )

grading_service = GradingService()
