from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from datetime import datetime

class MeasuredEvidence(BaseModel):
    rot_decay_ratio_pct: float = Field(..., description="Measured dark decay/browning percentage on produce area")
    discoloration_ratio_pct: float = Field(..., description="Measured mold/discoloration percentage on produce area")
    lesion_texture_density_pct: float = Field(..., description="Measured surface lesion/edge defect density")
    colour_vibrancy_score: int = Field(..., ge=0, le=100, description="1. COLOUR: Measured HSV colour vibrancy score 0-100")
    produce_size_scale_score: int = Field(..., ge=0, le=100, description="2. SIZE: Measured produce scale and frame volume occupancy 0-100")
    surface_smoothness_score: int = Field(..., ge=0, le=100, description="3. SURFACE DEFECTS: Measured surface defect-free score 0-100")
    visual_maturity_score: int = Field(..., ge=0, le=100, description="4. APPARENT MATURITY: Measured visual ripeness/maturity score 0-100")

class VisibleFactors(BaseModel):
    colour: int = Field(..., ge=0, le=100, description="Colour vibrancy parameter")
    size: int = Field(..., ge=0, le=100, description="Size & scale parameter")
    surface_condition: int = Field(..., ge=0, le=100, description="Surface defects parameter")
    maturity: int = Field(..., ge=0, le=100, description="Apparent maturity parameter")

class ImageQualityDetails(BaseModel):
    sharpness: float
    brightness: float
    contrast: float
    framing_score: float
    passed: bool
    reason: Optional[str] = None

class InspectionResponse(BaseModel):
    inspection_id: str
    batch_id: Optional[str] = None
    produce_type: str
    category: str  # "Fruit" or "Vegetable"
    raw_model_prediction: str  # "Fresh", "Defective", "Adulterant", "Rotten"
    quality: str   # "Fresh" or "Not Fresh"
    grade: str     # "A", "B", "C"
    quality_score: int  # 0-100
    confidence: float   # 0.0-1.0
    measured_evidence: MeasuredEvidence
    visible_factors: VisibleFactors
    defects: List[str]
    evidence_reasoning: str
    recommendation: str
    model_used: str
    grading_disclaimer: str
    image_quality_passed: bool
    image_quality_details: ImageQualityDetails
    image_url: Optional[str] = None
    timestamp: str
    is_demo: bool = False
