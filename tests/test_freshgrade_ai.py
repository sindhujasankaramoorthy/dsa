import pytest
import numpy as np
import cv2
import base64
from fastapi.testclient import TestClient
from backend.main import app
from backend.app.services.image_quality_service import image_quality_service
from backend.app.services.grading_service import grading_service
from backend.app.services.recommendation_service import recommendation_service
from backend.app.services.inference_service import inference_service
from backend.app.database.mongodb import db_manager

client = TestClient(app)

def create_synthetic_image(color=(50, 180, 50), width=300, height=300, add_blur=False, add_dark=False):
    """Creates synthetic image numpy array with high contrast features for testing."""
    img = np.zeros((height, width, 3), dtype=np.uint8)
    img[:] = color
    # Add sharp circle and text to simulate produce details and high sharpness
    cv2.circle(img, (150, 150), 90, (0, 0, 220), -1)
    cv2.putText(img, "PRODUCE", (50, 160), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255), 2)
    
    if add_dark:
        img = (img * 0.1).astype(np.uint8)
    if add_blur:
        img = cv2.GaussianBlur(img, (25, 25), 0)
    return img

def encode_image_to_base64(img_np):
    _, buf = cv2.imencode('.jpg', img_np)
    return base64.b64encode(buf.tobytes()).decode('utf-8')

class TestFreshGradeAI:

    def test_health_check(self):
        """Test API health endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "FreshGrade AI" in data["service"]

    def test_image_quality_validation_valid(self):
        """Test image reliability validation with a sharp, well-lit synthetic image."""
        img = create_synthetic_image(color=(50, 180, 50))
        passed, msg, details = image_quality_service.validate_image(img)
        assert passed is True
        assert details["sharpness"] > 0
        assert details["passed"] is True

    def test_image_quality_validation_dark_failure(self):
        """Test image reliability layer rejecting dark images."""
        img = create_synthetic_image(add_dark=True)
        passed, msg, details = image_quality_service.validate_image(img)
        assert passed is False
        assert "insufficient" in msg or "dark" in details.get("reason", "").lower()

    def test_grade_mapping_and_score(self):
        """Test evidence-first A/B/C grade mapping and measured evidence factors computation."""
        img = create_synthetic_image()
        evidence_fresh = {"rot_ratio_pct": 0.5, "discolor_ratio_pct": 1.0, "defect_density_pct": 2.0, "avg_sat": 140.0}
        
        grade_a, label_a, score_a, conf_a, me_a, factors_a, defects_a, reason_a = (
            grading_service.compute_grade_and_score("Fresh", 0.95, img, evidence_fresh)
        )
        assert grade_a == "A"
        assert score_a >= 80
        assert "rot ratio" in reason_a.lower()

        evidence_rotten = {"rot_ratio_pct": 12.5, "discolor_ratio_pct": 18.0, "defect_density_pct": 9.0, "avg_sat": 30.0}
        grade_c, label_c, score_c, conf_c, me_c, factors_c, defects_c, reason_c = (
            grading_service.compute_grade_and_score("Rotten", 0.90, img, evidence_rotten)
        )
        assert grade_c == "C"
        assert score_c < 50
        assert "12.5%" in reason_c or "dark decay" in reason_c.lower()

    def test_recommendation_service(self):
        """Test business sorting recommendation engine."""
        rec_a = recommendation_service.get_single_recommendation("Tomato", "A", 90)
        assert "premium retail" in rec_a.lower()

        rec_c = recommendation_service.get_single_recommendation("Potato", "C", 30)
        assert "processing" in rec_c.lower() or "secondary" in rec_c.lower()

    def test_produce_routing(self):
        """Test classification routing between Fruits and Vegetables."""
        img = create_synthetic_image()
        res_veg = inference_service.detect_produce_type_and_category(img, hint="Tomato")
        assert res_veg[1] == "Vegetable"

        res_fruit = inference_service.detect_produce_type_and_category(img, hint="Apple")
        assert res_fruit[1] == "Fruit"

    def test_inspect_api_endpoint(self):
        """Test POST /api/inspect endpoint returning evidence metrics and reasoning."""
        img = create_synthetic_image()
        b64 = encode_image_to_base64(img)
        
        response = client.post("/api/inspect", data={
            "image_base64": b64,
            "produce_hint": "Tomato",
            "demo_mode": "true"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        res = data["result"]
        assert res["produce_type"] == "Tomato"
        assert res["grade"] in ["A", "B", "C"]
        assert "measured_evidence" in res
        assert "evidence_reasoning" in res
        assert "grading_disclaimer" in res
        assert 0 <= res["quality_score"] <= 100

    def test_batch_api_workflow(self):
        """Test Batch Creation, Inspection, and Summary Aggregation."""
        create_res = client.post("/api/batches", json={
            "batch_name": "Test Tomato Batch",
            "produce_type": "Tomato",
            "category": "Vegetable"
        })
        assert create_res.status_code == 200
        batch = create_res.json()["batch"]
        batch_id = batch["batch_id"]

        img = create_synthetic_image()
        b64 = encode_image_to_base64(img)
        inspect_res = client.post(f"/api/batches/{batch_id}/inspect", data={
            "image_base64": b64,
            "produce_hint": "Tomato",
            "demo_mode": "true"
        })
        assert inspect_res.status_code == 200

        summary_res = client.get(f"/api/batches/{batch_id}")
        assert summary_res.status_code == 200
        sum_data = summary_res.json()
        assert sum_data["total_inspected"] >= 1
        assert sum_data["batch_id"] == batch_id

    def test_dashboard_api(self):
        """Test GET /api/dashboard endpoint."""
        res = client.get("/api/dashboard")
        assert res.status_code == 200
        data = res.json()
        assert data["success"] is True
        assert "total_inspections" in data["metrics"]

    def test_grade_to_industry_guide_destinations(self):
        """Test Grade-to-Industry destination routing for Grade A, B, C (Severe vs Cosmetic)."""
        from backend.app.services.industry_guide_service import industry_guide_service
        
        # Grade A
        res_a = industry_guide_service.evaluate_destination("Tomato", "A", quality_score=90)
        assert res_a["destination_category"] == "FRESH_MARKET"
        assert "Fresh Market" in res_a["title_en"]
        assert "Find Fresh Buyers" in res_a["button_label_en"]

        # Grade B
        res_b = industry_guide_service.evaluate_destination("Tomato", "B", quality_score=65)
        assert res_b["destination_category"] == "PROCESSING_WHOLESALE"
        assert "Processing / Wholesale" in res_b["title_en"]
        assert "Find Processing Buyers" in res_b["button_label_en"]

        # Grade C - Cosmetic Blemishes
        res_c_cosmetic = industry_guide_service.evaluate_destination(
            "Tomato", "C", defects=["Minor skin blemishes", "Irregular shape"], quality_score=50
        )
        assert res_c_cosmetic["destination_category"] == "FURTHER_ASSESSMENT_REQUIRED"
        assert "Further Assessment Required" in res_c_cosmetic["title_en"]

        # Grade C - Severe Rot / Deterioration
        res_c_severe = industry_guide_service.evaluate_destination(
            "Tomato", "C", defects=["Severe decay", "Fungal mould"], measured_evidence={"rot_decay_ratio_pct": 14.0}, quality_score=20
        )
        assert res_c_severe["destination_category"] == "NOT_RECOMMENDED_PROCESSING"
        assert "Not Recommended for Food Processing" in res_c_severe["title_en"]

    def test_industry_guide_api_evaluate(self):
        """Test POST /api/industry-guide/evaluate API endpoint."""
        res = client.post("/api/industry-guide/evaluate", json={
            "produce_name": "Tomato",
            "grade": "B",
            "quality_score": 70,
            "defects": ["Minor surface scratches"],
            "grade_a_kg": 55,
            "grade_b_kg": 30,
            "grade_c_kg": 15
        })
        assert res.status_code == 200
        data = res.json()
        assert data["success"] is True
        assert data["destination_guide"]["destination_category"] == "PROCESSING_WHOLESALE"
        assert data["batch_guidance"]["total_quantity_kg"] == 100.0
        assert len(data["buyer_records"]) > 0

