import cv2
import os
import sys

# Add the parent directory to sys.path so we can import src modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.pipeline import ANPRPipeline

def debug_segmentation():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(base_dir)
    img_path = r"D:\Num_Plate\State-wise_OLX\MH\MH1.jpg"
    
    if not os.path.exists(img_path):
        print("Image not found")
        return
        
    pipeline = ANPRPipeline()
    print("Detecting plate...")
    cropped_plate = pipeline.detector.detect_plate(img_path)
    
    if cropped_plate is None:
        print("No plate detected by YOLO!")
        return
        
    # Save YOLO crop for inspection
    cv2.imwrite(os.path.join(project_root, "debug_yolo_crop.jpg"), cropped_plate)
    print("Saved debug_yolo_crop.jpg")
    
    # Run segmentation
    print("Running preprocessor...")
    
    img = cropped_plate
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5,5), 0)
    _, thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    
    cv2.imwrite(os.path.join(project_root, "debug_thresh.jpg"), thresh)
    print("Saved debug_thresh.jpg")
    
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    print(f"Found {len(contours)} initial contours")
    
    img_contours = img.copy()
    cv2.drawContours(img_contours, contours, -1, (0, 255, 0), 1)
    cv2.imwrite(os.path.join(project_root, "debug_all_contours.jpg"), img_contours)
    
    bounding_boxes = []
    
    for c in contours:
        x, y, w, h = cv2.boundingRect(c)
        aspect_ratio = w / float(h)
        
        # Draw all bounding boxes in red
        cv2.rectangle(img_contours, (x, y), (x+w, y+h), (0, 0, 255), 1)
        
        if 0.1 < aspect_ratio < 1.5 and h > 10: 
            bounding_boxes.append((x, y, w, h))
            
    cv2.imwrite(os.path.join(project_root, "debug_boxes.jpg"), img_contours)
    print(f"Filtered to {len(bounding_boxes)} character boxes")

if __name__ == "__main__":
    debug_segmentation()
