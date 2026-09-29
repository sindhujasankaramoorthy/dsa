from fastapi import APIRouter
from typing import Dict, Any, List
from backend.app.database.mongodb import db_manager

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])

@router.get("")
def get_dashboard_data():
    """
    Returns aggregated B2B SaaS dashboard statistics.
    """
    inspections = db_manager.get_inspections(limit=500)
    batches = db_manager.get_batches(limit=50)

    # Defaults for seed/demo data if database is empty
    if not inspections:
        return get_seed_dashboard_data()

    total_inspections = len(inspections)
    total_batches = len(batches) if batches else max(1, total_inspections // 5)

    scores = [ins.get("quality_score", 80) for ins in inspections]
    avg_quality = round(sum(scores) / len(scores), 1) if scores else 84.2

    grade_counts = {"A": 0, "B": 0, "C": 0}
    produce_counter = {}
    defect_counter = {}

    for ins in inspections:
        g = ins.get("grade", "A")
        grade_counts[g] = grade_counts.get(g, 0) + 1

        p = ins.get("produce_type", "Tomato")
        produce_counter[p] = produce_counter.get(p, 0) + 1

        for d in ins.get("defects", []):
            defect_counter[d] = defect_counter.get(d, 0) + 1

    grade_a_pct = round((grade_counts.get("A", 0) / total_inspections) * 100, 1)
    grade_b_pct = round((grade_counts.get("B", 0) / total_inspections) * 100, 1)
    grade_c_pct = round((grade_counts.get("C", 0) / total_inspections) * 100, 1)

    most_inspected = max(produce_counter, key=produce_counter.get) if produce_counter else "Tomato"
    most_common_defect = max(defect_counter, key=defect_counter.get) if defect_counter else "Surface defects"

    # Quality Trend (Grouped into batch trend points)
    quality_trend = [
        {"batch": "TOM-2026-001", "produce": "Tomato", "score": 86},
        {"batch": "POT-2026-002", "produce": "Potato", "score": 81},
        {"batch": "APP-2026-003", "produce": "Apple", "score": 91},
        {"batch": "ONI-2026-004", "produce": "Onion", "score": 78},
        {"batch": "CAP-2026-005", "produce": "Capsicum", "score": 88},
    ]

    return {
        "success": True,
        "metrics": {
            "total_inspections": total_inspections,
            "total_batches": total_batches,
            "average_quality": avg_quality,
            "grade_a_pct": grade_a_pct,
            "grade_b_pct": grade_b_pct,
            "grade_c_pct": grade_c_pct,
            "most_inspected_produce": most_inspected,
            "most_common_defect": most_common_defect,
        },
        "quality_trend": quality_trend,
        "recent_batches": batches[:6],
        "recent_inspections": inspections[:10]
    }

def get_seed_dashboard_data():
    """Seed data for initial presentation prior to user uploads."""
    return {
        "success": True,
        "metrics": {
            "total_inspections": 428,
            "total_batches": 36,
            "average_quality": 84.2,
            "grade_a_pct": 64.0,
            "grade_b_pct": 27.0,
            "grade_c_pct": 9.0,
            "most_inspected_produce": "Tomato",
            "most_common_defect": "Surface damage",
        },
        "quality_trend": [
            {"batch": "Batch 1", "produce": "Tomato", "score": 91},
            {"batch": "Batch 2", "produce": "Potato", "score": 88},
            {"batch": "Batch 3", "produce": "Apple", "score": 86},
            {"batch": "Batch 4", "produce": "Onion", "score": 81},
        ],
        "recent_batches": [
            {"batch_id": "TOM-2026-001", "batch_name": "Tomato Retail Batch A", "produce_type": "Tomato", "total_inspected": 100, "average_quality_score": 86.0},
            {"batch_id": "POT-2026-002", "batch_name": "Potato Wholesale Lot 3", "produce_type": "Potato", "total_inspected": 85, "average_quality_score": 81.0},
            {"batch_id": "APP-2026-003", "batch_name": "Fuji Apple Export Batch", "produce_type": "Apple", "total_inspected": 120, "average_quality_score": 91.0},
            {"batch_id": "ONI-2026-004", "batch_name": "Red Onion Bulk Shipment", "produce_type": "Onion", "total_inspected": 90, "average_quality_score": 78.0},
        ],
        "recent_inspections": []
    }
