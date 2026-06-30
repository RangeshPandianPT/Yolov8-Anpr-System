import cv2
from ultralytics import YOLO
import os


class PlateDetector:
    def __init__(self, model_path='models/yolo_plate.pt'):
        """
        Initialize the YOLOv8 model for license plate detection.
        """
        self.model_path = model_path
        if os.path.exists(self.model_path):
            self.model = YOLO(self.model_path)
        else:
            self.model = None

    def detect_plate(self, image_path=None, image_array=None):
        """
        Detect and crop the license plate from an image.
        Returns a dict with status and metadata.
        """
        if image_array is not None:
            img = image_array
        elif image_path is not None:
            img = cv2.imread(image_path)
        else:
            return {"status": "error", "reason": "invalid_input", "message": "No input provided"}
            
        if img is None:
            return {
                "status": "error",
                "reason": "invalid_image",
                "message": "Unable to read the image file or array.",
            }
            
        if self.model is None:
            return {
                "status": "error",
                "reason": "model_not_loaded",
                "message": f"Detection model not found at '{self.model_path}'.",
            }

        results = self.model(img)

        for result in results:
            boxes = result.boxes
            if len(boxes) > 0:
                x1, y1, x2, y2 = map(int, boxes[0].xyxy[0])
                confidence = float(boxes[0].conf[0]) if boxes[0].conf is not None else None
                cropped_plate = img[y1:y2, x1:x2]

                if cropped_plate.size == 0:
                    return {
                        "status": "error",
                        "reason": "invalid_bbox",
                        "message": "Detected bounding box produced an empty crop.",
                        "confidence": confidence,
                        "bbox": [x1, y1, x2, y2],
                    }

                return {
                    "status": "success",
                    "plate_image": cropped_plate,
                    "confidence": confidence,
                    "bbox": [x1, y1, x2, y2],
                }

        return {
            "status": "error",
            "reason": "no_plate_detected",
            "message": "No plate-like object detected in the image.",
        }

if __name__ == "__main__":
    # Test stub
    pass
