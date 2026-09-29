from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from datetime import datetime
from backend.app.schemas.inspection import InspectionResponse

class BatchCreateRequest(BaseModel):
    batch_name: str
    produce_type: str
    category: str
    supplier_name: Optional[str] = "Standard Wholesale"
    notes: Optional[str] = None

class BatchSummaryResponse(BaseModel):
    batch_id: str
    batch_name: str
    produce_type: str
    category: str
    created_at: str
    total_inspected: int
    grade_counts: Dict[str, int]  # {"A": 62, "B": 29, "C": 9}
    grade_percentages: Dict[str, float]
    average_quality_score: float
    most_common_defect: str
    defects_breakdown: Dict[str, int]
    recommendation: str
    inspections: List[InspectionResponse] = []
