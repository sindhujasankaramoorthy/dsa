import os
import json
import logging
import base64
from typing import Dict, Any, Optional
import cv2
import numpy as np

logger = logging.getLogger("freshgrade.gemini_service")

SYSTEM_PROMPT = """
You are an expert Agricultural Quality Inspector and Computer Vision AI.
Analyze the provided produce image (fruit or vegetable) and evaluate its physical quality.

Return ONLY a valid JSON object matching the following structure (no markdown formatting, no code block backticks):
{
  "produce_type": "<Identified Fruit or Vegetable Name, e.g. Banana, Tomato, Apple>",
  "category": "<Fruit or Vegetable>",
  "quality": "<FRESH or NOT FRESH>",
  "grade": "<A, B, or C>",
  "quality_score": <Integer from 0 to 100>,
  "confidence": <Float from 0.70 to 0.99>,
  "visible_factors": {
    "colour": <Integer 0-100 score for colour vibrancy & uniformity>,
    "size": <Integer 0-100 score for size & frame occupancy>,
    "surface_condition": <Integer 0-100 score for defect-free surface smoothness>,
    "maturity": <Integer 0-100 score for visual maturity appropriateness>
  },
  "measured_evidence": {
    "rot_decay_ratio_pct": <Float percentage of rot/decay area, e.g. 7.5>,
    "discoloration_ratio_pct": <Float percentage of mold/discoloration area, e.g. 3.5>,
    "lesion_texture_density_pct": <Float percentage density of surface lesions, e.g. 2.1>,
    "colour_vibrancy_score": <Integer 0-100>,
    "produce_size_scale_score": <Integer 0-100>,
    "surface_smoothness_score": <Integer 0-100>,
    "visual_maturity_score": <Integer 0-100>
  },
  "defects": [
    "<Description of defect 1 if any>",
    "<Description of defect 2 if any>"
  ],
  "evidence_reasoning": "<Detailed, evidence-grounded 2-sentence explanation of why this grade and quality score were assigned based on visible colour, size, decay, or defects.>",
  "recommendation": {
    "primary_action": "<Consumer/Facility Action, e.g. Retail Premium Sale, Processing / Juicing, or Immediate Disposal>",
    "shelf_life_days": <Estimated remaining shelf life in days>,
    "storage_condition": "<Recommended storage temperature and conditions>",
    "destination": "<Optimal supply chain channel>"
  }
}

STRICT GRADING RULES:
1. If the produce shows visible rot, dark decay, mold, heavy skin discoloration, or severe structural damage:
   - quality MUST BE "NOT FRESH"
   - grade MUST BE "C" (or "B" if minor cosmetic damage only)
   - quality_score MUST BE between 10 and 38 for Grade C (e.g. 22/100) or 40-60 for Grade B. NEVER assign >65 score to rotten or moldy produce!
2. If the produce is clean, vibrant, firm, and defect-free:
   - quality MUST BE "FRESH"
   - grade MUST BE "A"
   - quality_score MUST BE between 75 and 98.
"""

class GeminiInspectionService:
    """Multimodal Vision Quality Inspection Engine powered by Google Gemini AI API."""

    def is_configured(self, api_key: Optional[str] = None) -> bool:
        key = api_key or os.getenv("GEMINI_API_KEY")
        return bool(key and len(key.strip()) > 10)

    def analyze_with_gemini(
        self,
        image_bytes: bytes,
        api_key: str,
        produce_hint: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Sends produce image to Gemini Vision API and returns structured quality grading payload.
        """
        key = api_key.strip() if api_key else os.getenv("GEMINI_API_KEY", "").strip()
        if not key:
            return None

        # Try Google GenAI SDK first, then google-generativeai fallback
        try:
            return self._call_google_genai(image_bytes, key, produce_hint)
        except Exception as e1:
            logger.warning(f"google-genai call failed: {e1}, attempting fallback via google-generativeai...")
            try:
                return self._call_google_generativeai(image_bytes, key, produce_hint)
            except Exception as e2:
                logger.error(f"Gemini API call failed: {e2}")
                return None

    def _call_google_genai(self, image_bytes: bytes, api_key: str, produce_hint: Optional[str]) -> Dict[str, Any]:
        from google import genai
        from google.genai import types

        client = genai.Client(api_key=api_key)
        prompt_text = SYSTEM_PROMPT
        if produce_hint:
            prompt_text += f"\nNote: The user claims this produce item is a '{produce_hint}'."

        image_part = types.Part.from_bytes(
            data=image_bytes,
            mime_type="image/jpeg"
        )

        # Try gemini-2.5-flash or fallback model
        models_to_try = ["gemini-2.5-flash", "gemini-1.5-flash-latest", "gemini-1.5-flash"]
        response = None
        last_err = None

        for model in models_to_try:
            try:
                response = client.models.generate_content(
                    model=model,
                    contents=[image_part, prompt_text]
                )
                if response and response.text:
                    break
            except Exception as ex:
                last_err = ex
                continue

        if not response or not response.text:
            raise RuntimeError(f"No response text from Gemini SDK: {last_err}")

        return self._parse_json_response(response.text, "google-genai-vision")

    def _call_google_generativeai(self, image_bytes: bytes, api_key: str, produce_hint: Optional[str]) -> Dict[str, Any]:
        import google.generativeai as genai
        from PIL import Image
        import io

        genai.configure(api_key=api_key)
        image = Image.open(io.BytesIO(image_bytes))

        prompt_text = SYSTEM_PROMPT
        if produce_hint:
            prompt_text += f"\nNote: The user claims this produce item is a '{produce_hint}'."

        models_to_try = ["gemini-2.5-flash", "gemini-1.5-flash-latest", "gemini-1.5-flash"]
        response = None
        last_err = None

        for m_name in models_to_try:
            try:
                model = genai.GenerativeModel(m_name)
                response = model.generate_content([image, prompt_text])
                if response and response.text:
                    break
            except Exception as ex:
                last_err = ex
                continue

        if not response or not response.text:
            raise RuntimeError(f"No response text from google-generativeai: {last_err}")

        return self._parse_json_response(response.text, "google-generativeai-vision")

    def _parse_json_response(self, text: str, model_used: str) -> Dict[str, Any]:
        clean_text = text.strip()
        if clean_text.startswith("```json"):
            clean_text = clean_text[7:]
        if clean_text.startswith("```"):
            clean_text = clean_text[3:]
        if clean_text.endswith("```"):
            clean_text = clean_text[:-3]
        clean_text = clean_text.strip()

        data = json.loads(clean_text)
        data["model_used"] = f"Gemini Multimodal AI ({model_used})"
        return data

gemini_service = GeminiInspectionService()
