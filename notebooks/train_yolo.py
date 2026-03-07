import os
from ultralytics import YOLO
import shutil
from pathlib import Path

def main():
    base_dir = Path(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    dataset_yaml = base_dir / "yolo_dataset" / "yolo_dataset.yaml"
    models_dir = base_dir / "models"
    
    if not dataset_yaml.exists():
        print(f"Error: {dataset_yaml} not found.")
        return
        
    print(f"Loading YOLOv8n pretrained model...")
    # Load a model
    model = YOLO("yolov8n.pt")  # load a pretrained model (recommended for training)

    print(f"Starting training on {dataset_yaml}...")
    # Train the model
    # We use a relatively small number of epochs for demonstration/quick training. 
    # For a production system this should ideally be 50-100+
    results = model.train(
        data=str(dataset_yaml), 
        epochs=10, 
        imgsz=640,
        batch=16,
        device=0,
        workers=0,
        project=str(base_dir / "runs"),
        name="plate_detection"
    )
    
    # Copy the best weights to models/yolo_plate.pt
    best_weights_path = base_dir / "runs" / "plate_detection" / "weights" / "best.pt"
    if best_weights_path.exists():
        target_path = models_dir / "yolo_plate.pt"
        shutil.copy2(best_weights_path, target_path)
        print(f"Successfully copied trained weights to {target_path}")
    else:
        print("Could not find best.pt!")

if __name__ == "__main__":
    main()
