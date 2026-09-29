import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger("freshgrade.industry_guide_service")

SAFETY_DISCLAIMER_EN = (
    "Recommendations are based on visible characteristics from the image. "
    "Final acceptance, food safety, pricing, and processing suitability must be confirmed by the buyer/processor."
)

SAFETY_DISCLAIMER_TA = (
    "பரிந்துரைகள் புகைப்படத்தின் அடிப்படையில் பெறப்பட்ட பார்வை இயல்புகளை மட்டுமே குறிக்கும். "
    "இறுதி ஏற்பு, உணவு பாதுகாப்பு, விலை மற்றும் பதப்படுத்தும் தகுதி ஆகியவை வாங்குபவரால் நேரில் உறுதிப்படுத்தப்பட வேண்டும்."
)

# Demo Buyers Database
DEMO_BUYERS: List[Dict[str, Any]] = [
    {
        "id": "buyer_1",
        "name": "ABC Tomato Processing Co.",
        "type": "Tomato Processing Industry",
        "type_ta": "தக்காளி பதப்படுத்தும் ஆலை",
        "location": "Krishnagiri Industrial Estate",
        "distance_km": 18,
        "accepted_produce": ["Tomato", "Capsicum"],
        "accepted_grades": ["Grade B", "Selected Grade C"],
        "phone": "+91 98765 43210",
        "email": "procurement@abctomato.com",
        "verified_demo": True,
        "icon": "🏭",
        "category": "PROCESSING"
    },
    {
        "id": "buyer_2",
        "name": "Fresh Produce Wholesale Hub",
        "type": "Wholesale Market Mandi",
        "type_ta": "மொத்த வியாபார மண்டி",
        "location": "Koyambedu / Local Wholesale Mandi",
        "distance_km": 8,
        "accepted_produce": ["Tomato", "Apple", "Banana", "Potato", "Mango", "Orange", "Onion"],
        "accepted_grades": ["Grade A", "Grade B"],
        "phone": "+91 98400 11223",
        "email": "trade@freshwholesalers.in",
        "verified_demo": True,
        "icon": "🏪",
        "category": "FRESH"
    },
    {
        "id": "buyer_3",
        "name": "Kovai Food Puree & Sauce Corp",
        "type": "Canning & Puree Manufacturer",
        "type_ta": "உணவு பதப்படுத்தும் நிறுவனம்",
        "location": "Coimbatore Food Park",
        "distance_km": 24,
        "accepted_produce": ["Tomato", "Mango", "Apple", "Banana"],
        "accepted_grades": ["Grade B", "Selected Grade C"],
        "phone": "+91 97100 55667",
        "email": "supply@kovaifoods.com",
        "verified_demo": True,
        "icon": "🥫",
        "category": "PROCESSING"
    },
    {
        "id": "buyer_4",
        "name": "Metro Retail Hypermarket",
        "type": "Supermarket Chain Supplier",
        "type_ta": "சூப்பர் மார்க்கெட் சங்கிலி",
        "location": "City Central Mall",
        "distance_km": 5,
        "accepted_produce": ["Tomato", "Apple", "Banana", "Orange", "Mango"],
        "accepted_grades": ["Grade A"],
        "phone": "+91 99520 88990",
        "email": "fresh@metroretail.in",
        "verified_demo": True,
        "icon": "🛒",
        "category": "FRESH"
    },
    {
        "id": "buyer_5",
        "name": "GreenAgri Dehydration & Powder Industries",
        "type": "Vegetable Dehydration & Flakes",
        "type_ta": "காய்கறி உலர்த்தும் ஆலை",
        "location": "Salem Agri Cluster",
        "distance_km": 35,
        "accepted_produce": ["Onion", "Potato", "Tomato"],
        "accepted_grades": ["Grade B", "Grade C"],
        "phone": "+91 94432 77889",
        "email": "contact@greenagridehyd.com",
        "verified_demo": True,
        "icon": "🌬️",
        "category": "PROCESSING"
    },
    {
        "id": "buyer_6",
        "name": "Nilgiri Bio-Energy & Organic Fertilizer Unit",
        "type": "Biogas & Bio-Compost Facility",
        "type_ta": "உயிர் எரிவாயு மற்றும் உர நிறுவனம்",
        "location": "Erode Bio-Park",
        "distance_km": 42,
        "accepted_produce": ["Tomato", "Apple", "Banana", "Potato", "Mango", "Onion"],
        "accepted_grades": ["Severe Grade C", "Spoiled / Non-edible Waste"],
        "phone": "+91 93600 44556",
        "email": "intake@nilgiribio.org",
        "verified_demo": True,
        "icon": "♻️",
        "category": "NON_FOOD"
    }
]

# Configurable Processing Industry Suggestions by Produce Type
PROCESSING_SUGGESTIONS_MAP: Dict[str, List[Dict[str, Any]]] = {
    "Tomato": [
        {
            "icon": "🍅",
            "title": "Tomato Puree",
            "title_ta": "தக்காளி கூழ் (Puree)",
            "industry": "Tomato Processing Industry",
            "industry_ta": "தக்காளி பதப்படுத்தும் ஆலை",
            "possible_use": "Puree / Ketchup Base",
            "possible_use_ta": "சாஸ் மற்றும் சாறு தயாரிப்பு",
            "suitable_grade": "Grade B / Selected Grade C",
            "requirement": "Subject to buyer inspection & acidity check",
            "requirement_ta": "வாங்குபவர் நேரில் ஆய்வு செய்து அமிலத்தன்மை சரிபார்க்க வேண்டும்"
        },
        {
            "icon": "🥫",
            "title": "Tomato Paste",
            "title_ta": "தக்காளி பேஸ்ட் (Paste)",
            "industry": "Tomato Concentrate & Paste Facility",
            "industry_ta": "அடர்ந்த பேஸ்ட் தயாரிப்பு ஆலை",
            "possible_use": "Paste / Thick Sauce",
            "possible_use_ta": "தடவல் மற்றும் மசாலா பேஸ்ட்",
            "suitable_grade": "Grade B / Selected Grade C",
            "requirement": "Subject to buyer inspection & Brix level",
            "requirement_ta": "வாங்குபவர் ஆய்வு மற்றும் Brix அளவு சரிபார்ப்பு"
        },
        {
            "icon": "🍅",
            "title": "Tomato Sauce",
            "title_ta": "தக்காளி சாஸ் (Sauce)",
            "industry": "Food Processing & Condiments Co.",
            "industry_ta": "உணவு மசாலா ஆலை",
            "possible_use": "Sauce & Seasoning Mix",
            "possible_use_ta": "உணவு சாஸ் தயாரிப்பு",
            "suitable_grade": "Grade B",
            "requirement": "Subject to buyer inspection",
            "requirement_ta": "வாங்குபவர் பார்வை ஆய்வு"
        },
        {
            "icon": "🥫",
            "title": "Canning",
            "title_ta": "தக்காளி கேனிங் (Canning)",
            "industry": "Vegetable Canning Industry",
            "industry_ta": "காய்கறி கேனிங் ஆலை",
            "possible_use": "Peeled / Diced Canned Tomatoes",
            "possible_use_ta": "டின் அடைத்த தக்காளி",
            "suitable_grade": "Grade A / Grade B",
            "requirement": "Subject to buyer inspection for firm skin",
            "requirement_ta": "தோல் உறுதித்தன்மை ஆய்வு"
        }
    ],
    "Apple": [
        {
            "icon": "🍎",
            "title": "Apple Juice",
            "title_ta": "ஆப்பிள் ஜூஸ்",
            "industry": "Fruit Beverage Facility",
            "industry_ta": "பழச்சாறு ஆலை",
            "possible_use": "Fresh Juice / Concentrate",
            "possible_use_ta": "பழச்சாறு மற்றும் பானங்கள்",
            "suitable_grade": "Grade B / Selected Grade C",
            "requirement": "Subject to sugar content inspection",
            "requirement_ta": "இனிப்பு அளவு ஆய்வு"
        },
        {
            "icon": "🍾",
            "title": "Cider Vinegar",
            "title_ta": "ஆப்பிள் சைடர் வினிகர்",
            "industry": "Fermentation & Condiments Unit",
            "industry_ta": "நொதித்தல் ஆலை",
            "possible_use": "Apple Cider Vinegar",
            "possible_use_ta": "வினிகர் தயாரிப்பு",
            "suitable_grade": "Grade B / Grade C",
            "requirement": "Subject to processor fermentation standards",
            "requirement_ta": "நொதித்தல் தரக் கட்டுப்பாடு"
        },
        {
            "icon": "🥣",
            "title": "Apple Puree & Jam",
            "title_ta": "ஆப்பிள் ஜாம் மற்றும் கூழ்",
            "industry": "Jam & Confectionery Factory",
            "industry_ta": "ஜாம் மற்றும் மிட்டாய் நிறுவனம்",
            "possible_use": "Apple Sauce / Jam Base",
            "possible_use_ta": "ஜாம் தயாரிப்பு",
            "suitable_grade": "Grade B",
            "requirement": "Subject to buyer quality check",
            "requirement_ta": "கொள்முதலாளர் ஆய்வு"
        }
    ],
    "Banana": [
        {
            "icon": "🍌",
            "title": "Banana Puree",
            "title_ta": "வாழைப்பழக் கூழ்",
            "industry": "Baby Food & Puree Industry",
            "industry_ta": "குழந்தை உணவு தயாரிப்பு ஆலை",
            "possible_use": "Puree / Smoothie Base",
            "possible_use_ta": "ஸ்மூத்தி மற்றும் குழந்தை உணவு",
            "suitable_grade": "Grade B",
            "requirement": "Subject to buyer ripeness inspection",
            "requirement_ta": "பழுத்த நிலை ஆய்வு"
        },
        {
            "icon": "🍌",
            "title": "Banana Chips",
            "title_ta": "வாழைக்காய் சிப்ஸ்",
            "industry": "Snack Food Processing",
            "industry_ta": "நொறுக்குத் தீனி ஆலை",
            "possible_use": "Fried / Baked Chips",
            "possible_use_ta": "வாழை சிப்ஸ்",
            "suitable_grade": "Grade A / Grade B (Raw)",
            "requirement": "Subject to firm raw texture check",
            "requirement_ta": "காய் உறுதித்தன்மை சரிபார்ப்பு"
        },
        {
            "icon": "🌾",
            "title": "Banana Powder & Flour",
            "title_ta": "வாழைப்பொடி (Flour)",
            "industry": "Agri-Flour Mill & Health Foods",
            "industry_ta": "தானிய மற்றும் சுகாதார உணவு ஆலை",
            "possible_use": "Health Powder / Bakery Mix",
            "possible_use_ta": "சத்து மாவு தயாரிப்பு",
            "suitable_grade": "Grade B / Grade C",
            "requirement": "Subject to moisture content test",
            "requirement_ta": "ஈரப்பதம் ஆய்வு"
        }
    ],
    "Potato": [
        {
            "icon": "🥔",
            "title": "Potato Flakes & Powder",
            "title_ta": "உருளைக்கிழங்கு பொடி",
            "industry": "Dehydration Industry",
            "industry_ta": "உலர்த்தும் ஆலை",
            "possible_use": "Instant Flakes / Snack Binder",
            "possible_use_ta": "இன்ஸ்டன்ட் பொடி",
            "suitable_grade": "Grade B / Grade C",
            "requirement": "Subject to starch content check",
            "requirement_ta": "ஸ்டார்ச் அளவு ஆய்வு"
        },
        {
            "icon": "🍟",
            "title": "Chips & French Fries",
            "title_ta": "உருளைக்கிழங்கு சிப்ஸ்",
            "industry": "Snack Manufacturing Co.",
            "industry_ta": "நொறுக்குத் தீனி நிறுவனம்",
            "possible_use": "Fried Chips / Strips",
            "possible_use_ta": "பிரெஞ்ச் பிரைஸ் மற்றும் சிப்ஸ்",
            "suitable_grade": "Grade A / Grade B",
            "requirement": "Subject to size & defect-free inspection",
            "requirement_ta": "அளவு மற்றும் வடுவின்மை ஆய்வு"
        }
    ],
    "Mango": [
        {
            "icon": "🥭",
            "title": "Mango Pulp",
            "title_ta": "மாம்பழக் கூழ் (Pulp)",
            "industry": "Fruit Pulping & Beverage Unit",
            "industry_ta": "மாம்பழக் கூழ் ஆலை",
            "possible_use": "Beverage & Juice Concentrate",
            "possible_use_ta": "மாம்பழ சாறு மற்றும் பானங்கள்",
            "suitable_grade": "Grade B / Selected Grade C",
            "requirement": "Subject to brix & aroma inspection",
            "requirement_ta": "மணம் மற்றும் இனிப்பு நிலை ஆய்வு"
        },
        {
            "icon": "🥫",
            "title": "Mango Pickle",
            "title_ta": "மாங்காய் ஊறுகாய்",
            "industry": "Pickle & Condiments Factory",
            "industry_ta": "ஊறுகாய் நிறுவனம்",
            "possible_use": "Raw Mango Pickle",
            "possible_use_ta": "ஊறுகாய் தயாரிப்பு",
            "suitable_grade": "Grade A / Grade B (Raw)",
            "requirement": "Subject to acidity & firmness test",
            "requirement_ta": "புளிப்பு மற்றும் உறுதித்தன்மை ஆய்வு"
        }
    ],
    "Orange": [
        {
            "icon": "🍊",
            "title": "Orange Concentrate",
            "title_ta": "ஆரஞ்சு பழச்சாறு அடர்வு",
            "industry": "Citrus Juice Industry",
            "industry_ta": "சிட்ரஸ் பழச்சாறு ஆலை",
            "possible_use": "Juice Concentrate",
            "possible_use_ta": "பழச்சாறு தயாரிப்பு",
            "suitable_grade": "Grade B",
            "requirement": "Subject to acidity & juice yield test",
            "requirement_ta": "சாறு அளவு மற்றும் அமிலத்தன்மை ஆய்வு"
        }
    ],
    "Onion": [
        {
            "icon": "🧅",
            "title": "Dehydrated Onion Kibbled & Powder",
            "title_ta": "வெங்காயப் பொடி & உலர்ந்த வெங்காயம்",
            "industry": "Spice & Dehydration Plant",
            "industry_ta": "மசாலா மற்றும் உலர்த்தும் ஆலை",
            "possible_use": "Flakes / Dehydrated Powder",
            "possible_use_ta": "உலர்ந்த துண்டுகள் மற்றும் பொடி",
            "suitable_grade": "Grade B / Selected Grade C",
            "requirement": "Subject to buyer dry weight inspection",
            "requirement_ta": "உலர்ந்த எடை ஆய்வு"
        }
    ]
}


class IndustryGuideService:
    """Service handling Grade-to-Industry Guide, Selling Destinations, Buyers & Safety Rules."""

    def evaluate_destination(
        self,
        produce_name: str,
        grade: str,
        defects: List[str] = None,
        measured_evidence: Dict[str, Any] = None,
        quality_score: int = 80
    ) -> Dict[str, Any]:
        """
        Evaluates existing AI grade + detected visible defects and determines appropriate selling destination.
        """
        defects = defects or []
        evidence = measured_evidence or {}
        rot_ratio = evidence.get("rot_decay_ratio_pct", 0.0) or evidence.get("rot_ratio_pct", 0.0)

        is_severe_rot = (
            rot_ratio >= 5.0
            or quality_score < 35
            or any("rot" in d.lower() or "mould" in d.lower() or "fungal" in d.lower() or "spoilage" in d.lower() for d in defects)
        )

        grade_upper = (grade or "A").upper()

        if grade_upper == "A":
            dest_key = "FRESH_MARKET"
            icon = "🟢"
            title_en = "Fresh Market"
            title_ta = "நுகர்வோர் / காய்கறி சந்தை (Fresh Market)"
            destinations_en = [
                "Fresh vegetable wholesalers",
                "Retailers",
                "Local markets",
                "Supermarkets"
            ]
            destinations_ta = [
                "காய்கறி மொத்த வியாபாரிகள்",
                "சில்லறை விற்பனையாளர்கள்",
                "உள்ளூர் சந்தைகள்",
                "சூப்பர் மார்க்கெட்டுகள்"
            ]
            message_en = "This produce appears visually suitable for the fresh market."
            message_ta = "இந்த விளைச்சல் நுகர்வோர் மற்றும் காய்கறி சந்தைக்கு ஏற்றதாக பார்வை அளவில் தோன்றுகிறது."
            button_label_en = "Find Fresh Buyers"
            button_label_ta = "சந்தை வியாபாரிகளைக் கண்டறியவும்"

        elif grade_upper == "B":
            dest_key = "PROCESSING_WHOLESALE"
            icon = "🟡"
            title_en = "Processing / Wholesale"
            title_ta = "உணவு பதப்படுத்துதல் / மொத்த விற்பனை"
            destinations_en = [
                f"{produce_name} sauce manufacturers",
                f"{produce_name} puree manufacturers",
                f"{produce_name} paste manufacturers",
                "Canning / food-processing industries",
                "Wholesale buyers"
            ]
            destinations_ta = [
                f"{produce_name} சாஸ் தயாரிப்பாளர்கள்",
                f"{produce_name} கூழ் (Puree) ஆலைகள்",
                f"{produce_name} பேஸ்ட் தயாரிப்பாளர்கள்",
                "கேனிங் / உணவு பதப்படுத்தும் தொழிற்சாலைகள்",
                "மொத்த வியாபாரிகள்"
            ]
            message_en = (
                "This produce may have lower fresh-market value but could potentially be suitable "
                "for processing or wholesale, depending on the buyer's requirements."
            )
            message_ta = (
                "இந்த விளைச்சல் நேரடி சந்தை மதிப்பைக் காட்டிலும் குறைவு என்றாலும், "
                "உணவு பதப்படுத்துதல் அல்லது மொத்த வியாபாரத்திற்கு ஏற்றதாக இருக்கலாம்."
            )
            button_label_en = "Find Processing Buyers"
            button_label_ta = "பதப்படுத்தும் ஆலைகளைக் கண்டறியவும்"

        else: # Grade C
            if is_severe_rot:
                dest_key = "NOT_RECOMMENDED_PROCESSING"
                icon = "🔴"
                title_en = "Not Recommended for Food Processing"
                title_ta = "உணவு பதப்படுத்துதலுக்கு பரிந்துரைக்கப்படவில்லை"
                destinations_en = [
                    "Biogas generation plants",
                    "Organic composting units",
                    "Non-edible bio-fertilizer processing"
                ]
                destinations_ta = [
                    "உயிர் எரிவாயு (Biogas) உற்பத்தி மையம்",
                    "இயற்கை உரம் (Compost) தயாரிப்பு",
                    "உண்ணத் தகாத உரம்/கழிவு மறுசுழற்சி"
                ]
                message_en = (
                    "Severe visible deterioration was detected. "
                    "This produce should not be recommended for food processing based only on this image."
                )
                message_ta = (
                    "கடுமையான சேதம் அல்லது அழுகல் கண்டறியப்பட்டுள்ளது. "
                    "இந்த புகைப்படத்தின் அடிப்படையில் இதை உணவு பதப்படுத்துதலுக்கு பரிந்துரைக்க முடியாது."
                )
                button_label_en = "Find Non-Food / Bio-Recycling Units"
                button_label_ta = "உர / உயிர்வாயு மையங்களைக் கண்டறியவும்"
            else:
                dest_key = "FURTHER_ASSESSMENT_REQUIRED"
                icon = "🟠"
                title_en = "Further Assessment Required"
                title_ta = "கூடுதல் நேரடி பரிசீலனை தேவை"
                destinations_en = [
                    "Processing industry, subject to processor acceptance and food-safety requirements."
                ]
                destinations_ta = [
                    "உணவு பதப்படுத்தும் ஆலை (ஆலை உரிமையாளரின் நேரடி பரிசோதனை மற்றும் உணவு பாதுகாப்பு ஒப்புதலுக்கு உட்பட்டது)."
                ]
                message_en = (
                    "This produce may have alternative processing value, but the processor must inspect and approve it."
                )
                message_ta = (
                    "இந்த விளைச்சலுக்கு மாற்று பதப்படுத்தும் மதிப்பு இருக்கலாம், ஆனால் கொள்முதல் செய்வோர் నేரில் ஆய்வு செய்து ஒப்புதல் அளிக்க வேண்டும்."
                )
                button_label_en = "Find Alternative Processing Buyers"
                button_label_ta = "மாற்று ஆலைகளைக் கண்டறியவும்"

        # Fetch Processing Suggestions
        suggestions = self.get_processing_suggestions(produce_name, grade_upper)

        return {
            "produce_name": produce_name,
            "grade": grade_upper,
            "quality_score": quality_score,
            "is_severe_rot": is_severe_rot,
            "destination_category": dest_key,
            "icon": icon,
            "title_en": title_en,
            "title_ta": title_ta,
            "destinations_en": destinations_en,
            "destinations_ta": destinations_ta,
            "message_en": message_en,
            "message_ta": message_ta,
            "button_label_en": button_label_en,
            "button_label_ta": button_label_ta,
            "processing_suggestions": suggestions,
            "safety_disclaimer_en": SAFETY_DISCLAIMER_EN,
            "safety_disclaimer_ta": SAFETY_DISCLAIMER_TA
        }

    def get_processing_suggestions(self, produce_name: str, grade: str = "B") -> List[Dict[str, Any]]:
        """Fetch configurable processing industry suggestions for given produce."""
        p_name = produce_name.strip().title()
        suggestions = PROCESSING_SUGGESTIONS_MAP.get(p_name)
        
        if not suggestions:
            # Dynamic fallback suggestion template for any custom fruit/vegetable
            suggestions = [
                {
                    "icon": "🏭",
                    "title": f"{p_name} Puree / Juice",
                    "title_ta": f"{p_name} சாறு மற்றும் கூழ்",
                    "industry": f"{p_name} Processing Facility",
                    "industry_ta": f"{p_name} பதப்படுத்தும் ஆலை",
                    "possible_use": "Puree / Juice Concentrate",
                    "possible_use_ta": "சாறு மற்றும் கூழ் தயாரிப்பு",
                    "suitable_grade": "Grade B / Selected Grade C",
                    "requirement": "Subject to buyer inspection",
                    "requirement_ta": "வாங்குபவர் நேரில் ஆய்வு செய்ய வேண்டும்"
                },
                {
                    "icon": "🥫",
                    "title": f"{p_name} Dehydration / Powder",
                    "title_ta": f"{p_name} பொடி மற்றும் உலர்ந்த பொருள்கள்",
                    "industry": f"{p_name} Dehydration Plant",
                    "industry_ta": f"{p_name} உலர்த்தும் ஆலை",
                    "possible_use": "Flakes / Dehydrated Powder",
                    "possible_use_ta": "பொடி மற்றும் உலர்ந்த துண்டுகள்",
                    "suitable_grade": "Grade B / Grade C",
                    "requirement": "Subject to buyer quality check",
                    "requirement_ta": "தர ஆய்வு உட்பட்டது"
                }
            ]
        return suggestions

    def get_buyers(
        self,
        produce_name: Optional[str] = None,
        grade_filter: Optional[str] = None,
        category_filter: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Filter demo buyers directory based on crop, grade, or category."""
        results = []
        p_name = (produce_name or "").lower()

        for b in DEMO_BUYERS:
            # Check produce match
            if p_name and not any(p_name in item.lower() for item in b["accepted_produce"]):
                # Allow general buyers if no exact match
                if not any(cat in b["type"].lower() for cat in ["wholesale", "mandi", "retail", "bio"]):
                    continue

            # Category filter
            if category_filter and category_filter != "ALL":
                if category_filter == "FRESH" and b["category"] != "FRESH":
                    continue
                if category_filter == "PROCESSING" and b["category"] != "PROCESSING":
                    continue

            results.append(b)

        return results if results else DEMO_BUYERS

    def evaluate_batch_destinations(
        self,
        produce_name: str,
        grade_a_kg: float,
        grade_b_kg: float,
        grade_c_kg: float,
        grade_c_severe: bool = False
    ) -> Dict[str, Any]:
        """Provides batch-level guidance with split destinations and step-by-step next steps."""
        total_kg = grade_a_kg + grade_b_kg + grade_c_kg

        c_dest_en = "Not Recommended for Food Processing (Biogas / Compost)" if grade_c_severe else "Further Assessment / Potential Processing"
        c_dest_ta = "உணவு பதப்படுத்துதலுக்கு பரிந்துரைக்கப்படவில்லை (உயிரெரிவாயு / உரம்)" if grade_c_severe else "நேரடி ஆய்வுக்கு பின் மாற்று பதப்படுத்துதல்"
        c_icon = "🔴" if grade_c_severe else "🟠"

        split_destinations = [
            {
                "grade": "Grade A",
                "quantity_kg": grade_a_kg,
                "icon": "🟢",
                "destination_en": f"{grade_a_kg} kg → Fresh Market",
                "destination_ta": f"{grade_a_kg} கிலோ → நுகர்வோர் / காய்கறி சந்தை",
                "channel": "Wholesalers, Retailers & Supermarkets"
            },
            {
                "grade": "Grade B",
                "quantity_kg": grade_b_kg,
                "icon": "🟡",
                "destination_en": f"{grade_b_kg} kg → Potential Processing Buyers",
                "destination_ta": f"{grade_b_kg} கிலோ → உணவு பதப்படுத்தும் ஆலைகள்",
                "channel": "Puree, Paste, Sauce & Canning Industries"
            },
            {
                "grade": "Grade C",
                "quantity_kg": grade_c_kg,
                "icon": c_icon,
                "destination_en": f"{grade_c_kg} kg → {c_dest_en}",
                "destination_ta": f"{grade_c_kg} கிலோ → {c_dest_ta}",
                "channel": "Processor Inspection / Bio-Recycling"
            }
        ]

        next_steps_en = [
            "1. Sell Grade A to fresh-market buyers.",
            "2. Contact processing buyers for Grade B.",
            "3. Inspect Grade C before deciding its destination."
        ]

        next_steps_ta = [
            "1. முதல் ரகம் (Grade A) விளைச்சலை காய்கறி சந்தை வியாபாரிகளிடம் விற்கவும்.",
            "2. இரண்டாம் ரகம் (Grade B) விளைச்சலுக்கு உணவு பதப்படுத்தும் ஆலைகளைத் தொடர்பு கொள்ளவும்.",
            "3. மூன்றாம் ரகம் (Grade C) விளைச்சலை ஆலை ஏற்றுக்கொள்கிறதா என நேரில் ஆய்வு செய்து தீர்மானிக்கவும்."
        ]

        return {
            "produce_name": produce_name,
            "total_quantity_kg": round(total_kg, 1),
            "split_destinations": split_destinations,
            "suggested_next_steps_en": next_steps_en,
            "suggested_next_steps_ta": next_steps_ta,
            "safety_disclaimer_en": SAFETY_DISCLAIMER_EN,
            "safety_disclaimer_ta": SAFETY_DISCLAIMER_TA
        }


industry_guide_service = IndustryGuideService()
