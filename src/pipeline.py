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
        
        # 1. Detection
        print(f"Detecting plate in {image_path}...")
        cropped_plate = self.detector.detect_plate(image_path)
        
        if cropped_plate is None:
            return {"status": "error", "message": "No plate detected."}
            
        # 2. Segmentation
        print("Segmenting characters...")
        character_images = self.preprocessor.preprocess(cropped_plate)
        
        if not character_images:
            return {"status": "error", "message": "Failed to segment characters."}
            
        # 3. Recognition
        print("Recognizing characters...")
        predicted_text = self.recognizer.predict_characters(character_images)
        
        # 4. Verification
        print(f"Verifying plate: {predicted_text}...")
        is_authorized, best_match, distance = self.verifier.verify_plate(predicted_text)
        
        processing_time = time.time() - start_time
        
        result = {
            "status": "success",
            "predicted_plate": predicted_text,
            "is_authorized": is_authorized,
            "best_match_db": best_match,
            "distance": distance,
            "processing_time_sec": round(processing_time, 3)
        }
        
        return result

if __name__ == "__main__":
    pass
