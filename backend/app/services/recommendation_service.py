from typing import Dict, Any

class RecommendationService:
    """Provides operational business sorting recommendations for produce batches and single items."""

    def get_single_recommendation(self, produce_name: str, grade: str, quality_score: int) -> str:
        if grade == "A":
            return f"Suitable for premium retail & export channels. Maintain cold chain storage."
        elif grade == "B":
            return f"Recommended for standard local retail, quick sale discounting, or immediate supply contracts."
        else: # Grade C
            return f"Divert from fresh produce sales. Recommended for industrial processing, puree, or secondary channel utilization."

    def get_batch_recommendation(
        self, produce_name: str, total: int, grade_counts: Dict[str, int], avg_score: float
    ) -> str:
        pct_a = (grade_counts.get("A", 0) / total) * 100 if total > 0 else 0
        pct_b = (grade_counts.get("B", 0) / total) * 100 if total > 0 else 0
        pct_c = (grade_counts.get("C", 0) / total) * 100 if total > 0 else 0

        if pct_a >= 70:
            return f"High-grade batch ({pct_a:.1f}% Grade A). Recommended for direct supermarket & premium retail distribution."
        elif pct_a + pct_b >= 75:
            return f"Mixed quality batch ({pct_a:.1f}% Grade A, {pct_b:.1f}% Grade B). Sorting recommended prior to retail distribution."
        else:
            return f"Low visual quality batch ({pct_c:.1f}% Grade C). High risk of spoilage. Immediate processing channel diversion advised."

recommendation_service = RecommendationService()
