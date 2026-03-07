import cv2
from ultralytics import YOLO
import os

class PlateDetector:
    def __init__(self, model_path='models/yolo_plate.pt'):
        """
        Initialize the YOLOv8 model for license plate detection.
        """
        # Load the model if it exists, else we'll train one later
        self.model_path = model_path
        if os.path.exists(self.model_path):
            self.model = YOLO(self.model_path)
        else:
            self.model = None

    def detect_plate(self, image_path):
        """
        Detect and crop the license plate from an image.
        Returns the cropped plate image.
        """
        # Load image
        img = cv2.imread(image_path)
        if img is None:
            return None
            
        if self.model is None:
            # Fallback mock plate extraction (e.g. center crop)
            h, w = img.shape[:2]
            return img[h//3:2*h//3, w//4:3*w//4]
            
        # Perform inference
        results = self.model(img)
        
        # Process results (assuming the first bound box is the plate)
        for result in results:
            boxes = result.boxes
            if len(boxes) > 0:
                # Get the first box coordinates
                x1, y1, x2, y2 = map(int, boxes[0].xyxy[0])
                
                # Crop the plate from the image
                cropped_plate = img[y1:y2, x1:x2]
                return cropped_plate
                
        # Fallback if no boxes found
        h, w = img.shape[:2]
        return img[h//3:2*h//3, w//4:3*w//4]

if __name__ == "__main__":
    # Test stub
    pass
