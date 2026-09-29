import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger("freshgrade.farmer_decision_service")

TRANSLATIONS = {
    "en": {
        "sell_now": "SELL NOW",
        "sort_sell": "SORT & SELL SEPARATELY",
        "consider_alt": "CONSIDER ANOTHER SELLING OPTION",
        "disclaimer": "This recommendation is based on visual AI analysis and the information you provided. Actual market prices and produce quality may differ.",
        "why_title": "Why this recommendation?",
        "option1_title": "Option 1 — Sell Entire Batch As-Is",
        "option2_title": "Option 2 — Sort & Sell Separately",
        "option3_title": "Option 3 — Alternative Buyer / Processing",
        "net_value": "Estimated Net Value",
        "read_aloud": "🔊 Read Aloud"
    },
    "ta": {
        "sell_now": "உடனடியாக விற்கவும் (SELL NOW)",
        "sort_sell": "தரம் பிரித்து விற்கவும் (SORT & SELL)",
        "consider_alt": "மாற்று விற்பனை வழியை பரிசீலிக்கவும்",
        "disclaimer": "இந்த பரிந்துரை பார்வை வழி AI பகுப்பாய்வு மற்றும் நீங்கள் வழங்கிய தகவல்களின் அடிப்படையிலானது. உண்மையான சந்தை விலைகள் மாறுபடலாம்.",
        "why_title": "ஏன் இந்த பரிந்துரை?",
        "option1_title": "விருப்பம் 1 — முழு விளைச்சலையும் அப்படியே விற்கவும்",
        "option2_title": "விருப்பம் 2 — தரம் பிரித்து தனித்தனியாக விற்கவும்",
        "option3_title": "விருப்பம் 3 — மாற்று கொள்முதல் / ஜூஸ் தயாரிப்பு",
        "net_value": "மதிப்பிடப்பட்ட நிகர வருமானம்",
        "read_aloud": "🔊 உரக்கப் படிக்கவும்"
    }
}

class FarmerDecisionService:
    """Harvest-to-Market Decision Engine for Farmers."""

    def evaluate_farmer_batch(
        self,
        produce_name: str,
        total_quantity_kg: float,
        harvest_date: str,
        location: str,
        buyer_price_per_kg: float,
        alt_buyer_price_per_kg: Optional[float] = None,
        sorting_cost_per_kg: float = 2.0, # ₹2/kg labor cost for sorting
        transport_cost_flat: float = 500.0, # ₹500 transportation cost
        measured_evidence: Dict[str, Any] = None,
        grade: str = "A",
        quality_score: int = 85,
        defects: List[str] = None
    ) -> Dict[str, Any]:
        """
        Calculates grade breakdown (A/B/C kg), evaluates financial scenarios,
        and generates a practical next-step decision for the farmer.
        """
        rot_ratio = (measured_evidence or {}).get("rot_decay_ratio_pct", 1.0)
        discolor_ratio = (measured_evidence or {}).get("discoloration_ratio_pct", 1.0)

        # Estimate Grade Distribution (Kg) based on visual AI inspection
        if grade == "A" or quality_score >= 75:
            grade_a_pct = max(65.0, min(90.0, quality_score * 0.95))
            grade_b_pct = max(8.0, 100.0 - grade_a_pct - 3.0)
            grade_c_pct = max(2.0, 100.0 - grade_a_pct - grade_b_pct)
        elif grade == "B" or (quality_score >= 42 and quality_score < 75):
            grade_a_pct = 25.0
            grade_b_pct = 55.0
            grade_c_pct = 20.0
        else: # Grade C
            grade_a_pct = 10.0
            grade_b_pct = 30.0
            grade_c_pct = 60.0

        kg_a = round((grade_a_pct / 100.0) * total_quantity_kg, 1)
        kg_b = round((grade_b_pct / 100.0) * total_quantity_kg, 1)
        kg_c = round((grade_c_pct / 100.0) * total_quantity_kg, 1)
        usable_kg = round(kg_a + kg_b, 1)

        # Pricing Models (₹/kg)
        base_price = max(5.0, buyer_price_per_kg)
        price_a = round(base_price * 1.25, 2) # Premium Grade A commands +25%
        price_b = round(base_price * 0.90, 2) # Standard Grade B commands 90%
        price_c = round(base_price * 0.30, 2) # Damaged Grade C commands 30% (juicing/compost)
        alt_price = alt_buyer_price_per_kg or round(base_price * 1.10, 2)

        # Financial Scenario 1: Sell Entire Batch As-Is (No Sorting)
        gross_1 = round(total_quantity_kg * base_price, 2)
        sort_cost_1 = 0.0
        trans_cost_1 = transport_cost_flat
        net_1 = round(gross_1 - trans_cost_1, 2)

        # Financial Scenario 2: Sort & Sell Separately
        gross_2 = round((kg_a * price_a) + (kg_b * price_b) + (kg_c * price_c), 2)
        sort_cost_2 = round(total_quantity_kg * sorting_cost_per_kg, 2)
        trans_cost_2 = transport_cost_flat + 150.0 # extra handling
        net_2 = round(gross_2 - sort_cost_2 - trans_cost_2, 2)

        # Financial Scenario 3: Alternative Buyer / Juicing Facility
        gross_3 = round((usable_kg * alt_price) + (kg_c * price_c), 2)
        sort_cost_3 = round(total_quantity_kg * 0.5, 2)
        trans_cost_3 = transport_cost_flat + 300.0
        net_3 = round(gross_3 - sort_cost_3 - trans_cost_3, 2)

        # Decision Engine Logic
        sorting_gain = net_2 - net_1

        if grade_a_pct >= 70.0 and sorting_gain < 300:
            action_code = "SELL_NOW"
            action_title_en = "SELL NOW"
            action_title_ta = "உடனடியாக விற்கவும் (SELL NOW)"
            action_icon = "🟢"
            why_en = [
                f"{int(grade_a_pct)}% of your harvested batch appears visually market-ready (Grade A).",
                f"Only {int(grade_c_pct)}% shows visible damage.",
                f"Immediate selling avoids labor sorting costs and risk of rot during delay."
            ]
            why_ta = [
                f"உங்கள் விளைச்சலில் {int(grade_a_pct)}% தரமானதாக (Grade A) உள்ளது.",
                f"{int(grade_c_pct)}% மட்டுமே சேதமடைந்துள்ளது.",
                f"உடனடியாக விற்பது தரம் பிரிக்கும் கூலிச் செலவையும் அழுகல் அபாயத்தையும் தவிர்க்கும்."
            ]
        elif sorting_gain >= 300 and usable_kg >= 40:
            action_code = "SORT_AND_SELL"
            action_title_en = "SORT & SELL SEPARATELY"
            action_title_ta = "தரம் பிரித்து விற்கவும் (SORT & SELL)"
            action_icon = "🟡"
            why_en = [
                f"Sorting can increase your net earnings by approximately ₹{int(sorting_gain):,}.",
                f"You have {kg_a} kg of Premium Grade A produce which commands a higher price (₹{price_a}/kg).",
                f"Separating damaged produce ({kg_c} kg) prevents buyers from downgrading your entire lot."
            ]
            why_ta = [
                f"தரம் பிரித்து விற்பதன் மூலம் உங்களுக்கு சுமார் ₹{int(sorting_gain):,} கூடுதல் லாபம் கிடைக்கும்.",
                f"உங்களிடம் {kg_a} கிலோ முதல் ரக (Grade A) விளைச்சல் உள்ளது (ரூ.{price_a}/கிலோ).",
                f"சேதமடைந்த காய்களை ({kg_c} கிலோ) பிரிப்பது மொத்த விளைச்சலின் விலையைக் குறைப்பதைத் தடுக்கும்."
            ]
        else:
            action_code = "CONSIDER_ALT_BUYER"
            action_title_en = "CONSIDER ANOTHER SELLING OPTION"
            action_title_ta = "மாற்று விற்பனை வழியை பரிசீலிக்கவும்"
            action_icon = "🟠"
            why_en = [
                f"A significant portion ({int(grade_c_pct)}%) shows visible damage or deterioration.",
                f"Selling the entire batch to a single retail buyer may lead to high price cuts.",
                f"Consider selling Grade A/B to fresh markets and Grade C ({kg_c} kg) to local processing or juicing units."
            ]
            why_ta = [
                f"விளைச்சலில் கணிசமான அளவு ({int(grade_c_pct)}%) சேதமடைந்துள்ளது.",
                f"ஒரே வியாபாரியிடம் முழுமையாக விற்றால் அதிக விலை குறைப்பு ஏற்படலாம்.",
                f"நல்ல காய்களை சந்தையிலும், சேதமடைந்தவற்றை ({kg_c} கிலோ) ஜூஸ்/கழிவு மையத்திலும் விற்கலாம்."
            ]

        # Simple Farmer-Friendly Voice Scripts
        voice_en = (
            f"Recommended action: {action_title_en}. "
            f"Your harvested batch of {total_quantity_kg} kg tomatoes has {kg_a} kg premium quality and {kg_b} kg standard quality. "
            f"Estimated usable produce is {usable_kg} kg. {why_en[0]}"
        )
        voice_ta = (
            f"பரிந்துரைக்கப்பட்ட நடவடிக்கை: {action_title_ta}. "
            f"உங்கள் {total_quantity_kg} கிலோ விளைச்சலில் {kg_a} கிலோ முதல் ரகம் மற்றும் {kg_b} கிலோ இரண்டாம் ரகம் உள்ளது. "
            f"பயன்படுத்தக்கூடிய அளவு {usable_kg} கிலோ. {why_ta[0]}"
        )

        return {
            "produce_name": produce_name,
            "total_quantity_kg": total_quantity_kg,
            "harvest_date": harvest_date,
            "location": location,
            "buyer_price_per_kg": base_price,
            "quality_grade": grade,
            "quality_score": quality_score,

            # Grade Breakdown (Kg)
            "breakdown": {
                "grade_a_kg": kg_a,
                "grade_b_kg": kg_b,
                "grade_c_kg": kg_c,
                "usable_kg": usable_kg,
                "grade_a_pct": round(grade_a_pct, 1),
                "grade_b_pct": round(grade_b_pct, 1),
                "grade_c_pct": round(grade_c_pct, 1)
            },

            # Recommendation Card
            "recommendation": {
                "code": action_code,
                "icon": action_icon,
                "title_en": action_title_en,
                "title_ta": action_title_ta,
                "why_en": why_en,
                "why_ta": why_ta,
                "voice_en": voice_en,
                "voice_ta": voice_ta,
                "disclaimer_en": TRANSLATIONS["en"]["disclaimer"],
                "disclaimer_ta": TRANSLATIONS["ta"]["disclaimer"]
            },

            # Scenario What-If Matrix
            "scenarios": [
                {
                    "id": "option_1",
                    "title_en": "Option 1 — Sell Entire Batch As-Is",
                    "title_ta": "விருப்பம் 1 — முழுமையாக விற்கவும்",
                    "quantity_kg": total_quantity_kg,
                    "avg_price_per_kg": base_price,
                    "gross_revenue": gross_1,
                    "sorting_cost": sort_cost_1,
                    "transport_cost": trans_cost_1,
                    "net_estimated_value": net_1
                },
                {
                    "id": "option_2",
                    "title_en": "Option 2 — Sort & Sell Separately",
                    "title_ta": "விருப்பம் 2 — தரம் பிரித்து விற்கவும்",
                    "quantity_kg": total_quantity_kg,
                    "price_details": f"A: ₹{price_a} | B: ₹{price_b} | C: ₹{price_c}",
                    "gross_revenue": gross_2,
                    "sorting_cost": sort_cost_2,
                    "transport_cost": trans_cost_2,
                    "net_estimated_value": net_2
                },
                {
                    "id": "option_3",
                    "title_en": "Option 3 — Alternative Buyer / Juicing",
                    "title_ta": "விருப்பம் 3 — மாற்று கொள்முதல்",
                    "quantity_kg": total_quantity_kg,
                    "price_details": f"Market: ₹{alt_price} | Juicing: ₹{price_c}",
                    "gross_revenue": gross_3,
                    "sorting_cost": sort_cost_3,
                    "transport_cost": trans_cost_3,
                    "net_estimated_value": net_3
                }
            ]
        }

farmer_decision_service = FarmerDecisionService()
