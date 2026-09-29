import cv2
import numpy as np
from typing import Dict, Any, Tuple

class ImageQualityService:
    """Pre-grading image reliability validator checking blur, lighting, contrast, and framing."""
    
    MIN_SHARPNESS = 45.0      # Laplacian variance threshold
    MIN_BRIGHTNESS = 35.0     # Mean intensity threshold (too dark)
    MAX_BRIGHTNESS = 230.0    # Mean intensity threshold (too bright / overexposed)
    MIN_CONTRAST = 25.0       # Standard deviation of intensity
    MIN_PRODUCE_AREA_RATIO = 0.08  # Produce foreground must occupy at least 8% of frame

    def validate_image(self, image_np: np.ndarray) -> Tuple[bool, str, Dict[str, Any]]:
        if image_np is None or image_np.size == 0:
            return False, "Corrupt or invalid image data.", {
                "sharpness": 0.0, "brightness": 0.0, "contrast": 0.0, "framing_score": 0.0, "passed": False
            }

        # Convert to grayscale for statistical analysis
        if len(image_np.shape) == 3:
            gray = cv2.cvtColor(image_np, cv2.COLOR_BGR2GRAY)
        else:
            gray = image_np

        height, width = gray.shape

        # 1. Blur Detection (Laplacian Variance)
        laplacian_var = float(cv2.Laplacian(gray, cv2.CV_64F).var())

        # 2. Lighting / Illumination Check
        mean_brightness = float(np.mean(gray))

        # 3. Contrast Check
        contrast = float(np.std(gray))

        # 4. Produce Framing / Foreground Check
        # Otsu thresholding to estimate foreground produce presence
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        foreground_pixels = np.count_nonzero(thresh)
        area_ratio = float(foreground_pixels / (height * width))
        framing_score = min(100.0, max(0.0, area_ratio * 300.0))

        details = {
            "sharpness": round(laplacian_var, 2),
            "brightness": round(mean_brightness, 2),
            "contrast": round(contrast, 2),
            "framing_score": round(framing_score, 2),
            "passed": True,
            "reason": None
        }

        # Evaluate quality conditions
        if laplacian_var < self.MIN_SHARPNESS:
            details["passed"] = False
            details["reason"] = "Image is too blurry or out of focus."
            return False, "Image quality insufficient for reliable grading. Image is blurry. Please retake under steady lighting.", details

        if mean_brightness < self.MIN_BRIGHTNESS:
            details["passed"] = False
            details["reason"] = "Image lighting is too dark."
            return False, "Image quality insufficient for reliable grading. Image is too dark. Please retake under better lighting with the produce clearly visible.", details

        if mean_brightness > self.MAX_BRIGHTNESS:
            details["passed"] = False
            details["reason"] = "Image is overexposed or extremely bright."
            return False, "Image quality insufficient for reliable grading. Image is overexposed. Please avoid harsh glare.", details

        if contrast < self.MIN_CONTRAST:
            details["passed"] = False
            details["reason"] = "Low visual contrast in the frame."
            return False, "Image quality insufficient for reliable grading. Low contrast detected.", details

        return True, "Image quality passed reliability check.", details

image_quality_service = ImageQualityService()
