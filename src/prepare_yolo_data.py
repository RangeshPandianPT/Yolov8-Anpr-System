import os
import glob
import xml.etree.ElementTree as ET
import shutil
import random
import yaml
from pathlib import Path

def convert_voc_to_yolo(xml_file, classes=["number_plate"]):
    """
    Parses a Pascal VOC XML file and converts bounding boxes to YOLO format.
    Returns a list of YOLO format strings (class x_center y_center width height).
    """
    try:
        tree = ET.parse(xml_file)
        root = tree.getroot()
        
        size = root.find('size')
        if size is None:
            return None
        w = int(size.find('width').text)
        h = int(size.find('height').text)
        
        # If width or height is 0, skip
        if w == 0 or h == 0:
            return None

        yolo_labels = []
        for obj in root.iter('object'):
            difficult = obj.find('difficult')
            difficult = int(difficult.text) if difficult is not None else 0
            cls = obj.find('name').text
            if cls not in classes:
                # If name isn't exactly what we want, still count it as class 0 for number_plate
                cls_id = 0
            else:
                cls_id = classes.index(cls)
                
            xmlbox = obj.find('bndbox')
            xmin = float(xmlbox.find('xmin').text)
            xmax = float(xmlbox.find('xmax').text)
            ymin = float(xmlbox.find('ymin').text)
            ymax = float(xmlbox.find('ymax').text)
            
            # YOLO format: x_center, y_center, width, height (normalized)
            x_center = ((xmin + xmax) / 2.0) / w
            y_center = ((ymin + ymax) / 2.0) / h
            width = (xmax - xmin) / w
            height = (ymax - ymin) / h
            
            # Clip values between 0 and 1
            x_center = max(0.0, min(1.0, x_center))
            y_center = max(0.0, min(1.0, y_center))
            width = max(0.0, min(1.0, width))
            height = max(0.0, min(1.0, height))
            
            yolo_labels.append(f"{cls_id} {x_center:.6f} {y_center:.6f} {width:.6f} {height:.6f}")
            
        return yolo_labels
    except Exception as e:
        print(f"Error parsing {xml_file}: {e}")
        return None

def main():
    base_dir = Path(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    dataset_dir = base_dir / "yolo_dataset"
    
    # Create output directories
    images_train_dir = dataset_dir / "images" / "train"
    images_val_dir = dataset_dir / "images" / "val"
    labels_train_dir = dataset_dir / "labels" / "train"
    labels_val_dir = dataset_dir / "labels" / "val"
    
    for d in [images_train_dir, images_val_dir, labels_train_dir, labels_val_dir]:
        d.mkdir(parents=True, exist_ok=True)
        
    print(f"Created YOLO dataset directories in {dataset_dir}")
    
    # Find all XML files in the base directory
    print("Finding XML annotation files...")
    all_xml_files = list(base_dir.rglob("*.xml"))
    
    # Exclude files that might be in venv or other unrelated dirs
    xml_files = [str(f) for f in all_xml_files if 'venv' not in str(f) and 'yolo_dataset' not in str(f)]
    
    print(f"Found {len(xml_files)} XML files.")
    
    valid_data_pairs = []
    
    for xml_file in xml_files:
        xml_path = Path(xml_file)
        # Try to find the corresponding image
        # Sometimes the image is in the same directory, sometimes in an adjacent one.
        # Let's check common extensions in the same directory first
        found_img_path = None
        for ext in ['.jpg', '.jpeg', '.png', '.JPG', '.PNG']:
            img_candidate = xml_path.with_suffix(ext)
            if img_candidate.exists():
                found_img_path = img_candidate
                break
                
        if not found_img_path:
            # Let's check in typical sibling image folders if it's named 'Annotations'
            if xml_path.parent.name == 'Annotations':
                # Look for 'Images' folder next to 'Annotations' or in root
                pass
                
        # If we still haven't found it, try searching the entire tree for a file with the same stem
        if not found_img_path:
            stem = xml_path.stem
            # This is slow, but we only have a few hundred files
            for img_file in base_dir.rglob(f"{stem}.*"):
                if img_file.suffix.lower() in ['.jpg', '.jpeg', '.png'] and 'venv' not in str(img_file):
                    found_img_path = img_file
                    break
        
        if found_img_path:
            yolo_labels = convert_voc_to_yolo(xml_file)
            if yolo_labels is not None and len(yolo_labels) > 0:
                valid_data_pairs.append((str(found_img_path), str(xml_path), yolo_labels))
            else:
                print(f"Warning: No valid labels found in {xml_path}")
        else:
            print(f"Warning: Could not find corresponding image for {xml_path}")
            
    print(f"Successfully matched {len(valid_data_pairs)} valid image-label pairs.")
    
    # Shuffle and split
    random.shuffle(valid_data_pairs)
    split_idx = int(0.8 * len(valid_data_pairs))
    train_pairs = valid_data_pairs[:split_idx]
    val_pairs = valid_data_pairs[split_idx:]
    
    print(f"Splitting data: {len(train_pairs)} training, {len(val_pairs)} validation.")
    
    def copy_and_write(pairs, split_name):
        img_dir = images_train_dir if split_name == "train" else images_val_dir
        lbl_dir = labels_train_dir if split_name == "train" else labels_val_dir
        
        for k, (img_path, xml_path, labels) in enumerate(pairs):
            # We rename files minimally to ensure uniqueness if needed, but original names are usually fine
            # Let's use the original name but replace spaces or weird chars if any
            stem = Path(img_path).stem.replace(" ", "_").replace("(", "").replace(")", "")
            ext = Path(img_path).suffix
            
            # To completely avoid collision, appending index
            new_img_name = f"{stem}_{split_name}_{k}{ext}"
            new_lbl_name = f"{stem}_{split_name}_{k}.txt"
            
            dest_img_path = img_dir / new_img_name
            dest_lbl_path = lbl_dir / new_lbl_name
            
            # Copy image
            try:
                shutil.copy2(img_path, dest_img_path)
                # Write YOLO format label
                with open(dest_lbl_path, 'w') as f:
                    f.write("\n".join(labels))
            except Exception as e:
                print(f"Error copying {img_path}: {e}")

    print("Copying training files...")
    copy_and_write(train_pairs, "train")
    
    print("Copying validation files...")
    copy_and_write(val_pairs, "val")
    
    yaml_path = dataset_dir / "yolo_dataset.yaml"
    yaml_content = {
        'path': str(dataset_dir.absolute()),
        'train': 'images/train',
        'val': 'images/val',
        'test': '',
        'nc': 1,
        'names': ['number_plate']
    }
    
    with open(yaml_path, 'w') as f:
        yaml.dump(yaml_content, f, default_flow_style=False)
        
    print(f"Preparation complete! Created {yaml_path}")

if __name__ == "__main__":
    main()
