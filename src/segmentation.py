import cv2
import numpy as np

class PlatePreprocessor:
    def __init__(self):
        # Configuration for preprocessing
        pass

    def preprocess(self, img):
        """
        Convert plate image to grayscale, blur, threshold, and find character contours.
        Returns a list of character images sorted left-to-right.
        """
        # 1. Grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # 2. Gaussian Blur
        blur = cv2.GaussianBlur(gray, (5,5), 0)
        
        # 3. Thresholding (Adaptive or Otsu)
        _, thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        
        # 4. Find Contours
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        char_images = []
        bounding_boxes = []
        
        for c in contours:
            x, y, w, h = cv2.boundingRect(c)
            # Filter contours based on aspect ratio and size
            aspect_ratio = w / float(h)
            if 0.1 < aspect_ratio < 1.5 and h > 10: 
                bounding_boxes.append((x, y, w, h))
                
        # Sort left to right
        bounding_boxes = sorted(bounding_boxes, key=lambda b: b[0])
        
        for (x, y, w, h) in bounding_boxes:
            char_crop = thresh[y:y+h, x:x+w]
            # Resize character to standard size for CNN (e.g., 28x28)
            char_resized = cv2.resize(char_crop, (28, 28))
            char_images.append(char_resized)
            
        return char_images

if __name__ == "__main__":
    pass
