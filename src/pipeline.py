import cv2
import time
from .detection import PlateDetector
from .segmentation import PlatePreprocessor
from .recognition import CharacterRecognizer
from .database import PlateVerifier

class ANPRPipeline:
    def __init__(self):
        print("Initializing ANPR Pipeline Modules...")
        self.detector = PlateDetector()
        self.preprocessor = PlatePreprocessor()
        self.recognizer = CharacterRecognizer()
        self.verifier = PlateVerifier()
        print("Initialization Complete.")

    def process_image(self, image_path):
        """
        Run the full ANPR pipeline on a single image.
        """
        start_time = time.time()

        print(f"Detecting plate in {image_path}...")
        detection_result = self.detector.detect_plate(image_path)

        if detection_result.get("status") != "success":
            processing_time = time.time() - start_time
            return {
                "status": "error",
                "error_code": detection_result.get("reason", "detection_failed"),
                "message": detection_result.get("message", "Plate detection failed."),
                "processing_time_sec": round(processing_time, 3),
            }

        cropped_plate = detection_result["plate_image"]

        print("Segmenting characters...")
        character_images = self.preprocessor.preprocess(cropped_plate)

        if not character_images:
            processing_time = time.time() - start_time
            return {
                "status": "error",
                "error_code": "segmentation_failed",
                "message": "Failed to segment characters.",
                "detection_confidence": detection_result.get("confidence"),
                "processing_time_sec": round(processing_time, 3),
            }

        print("Recognizing characters...")
        predicted_text = self.recognizer.predict_characters(character_images)

        if not predicted_text:
            processing_time = time.time() - start_time
            return {
                "status": "error",
                "error_code": "ocr_empty_output",
                "message": "OCR output was empty.",
                "detection_confidence": detection_result.get("confidence"),
                "processing_time_sec": round(processing_time, 3),
            }

        print(f"Verifying plate: {predicted_text}...")
        is_authorized, best_match, distance = self.verifier.verify_plate(predicted_text)

        processing_time = time.time() - start_time

        result = {
            "status": "success",
            "predicted_plate": predicted_text,
            "is_authorized": is_authorized,
            "best_match_db": best_match,
            "distance": distance,
            "detection_confidence": detection_result.get("confidence"),
            "detection_bbox": detection_result.get("bbox"),
            "processing_time_sec": round(processing_time, 3)
        }

        return result

if __name__ == "__main__":
    pass
