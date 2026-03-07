import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import random
import numpy as np
import string
from pathlib import Path

def generate_synthetic_characters(output_dir, num_samples_per_class=200):
    """
    Generates a dataset of synthetic 28x28 character images (A-Z, 0-9).
    """
    classes = list(string.digits + string.ascii_uppercase)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Create class subdirectories
    for cls in classes:
        (output_dir / cls).mkdir(exist_ok=True)
        
    print(f"Generating synthetic character dataset in {output_dir}")
    
    # A generic font available on Windows / Google Colab
    # We'll try a few common ones
    font_paths = [
        "arial.ttf",
        "tahoma.ttf",
        "impact.ttf",
        "cour.ttf" # Courier New
    ]
    
    fonts = []
    for fp in font_paths:
        try:
            # Load font at different sizes
            for size in [20, 22, 24, 26]:
                fonts.append(ImageFont.truetype(fp, size))
        except IOError:
            continue
            
    if not fonts:
        print("Warning: Common fonts not found, falling back to default font.")
        fonts.append(ImageFont.load_default())
        
    generated_count = 0
    for cls in classes:
        for i in range(num_samples_per_class):
            # 1. Create a blank image with a random grayscale background
            bg_color = random.randint(0, 50)  # Dark background, assuming we want inverted or standard.
            # Usually plates have black text on white background, 
            # and preprocessing often thresholds to white text on black background (cv2.THRESH_BINARY_INV).
            # Let's generate images that look like the output of segmentation (white char on black bg)
            img = Image.new('L', (32, 32), color=bg_color)
            draw = ImageDraw.Draw(img)
            
            # 2. Draw text
            font = random.choice(fonts)
            text_color = random.randint(200, 255) # Bright white/gray
            
            # Get text bounding box to center it
            bbox = draw.textbbox((0, 0), cls, font=font)
            text_w = bbox[2] - bbox[0]
            text_h = bbox[3] - bbox[1]
            
            x = (32 - text_w) / 2 + random.randint(-2, 2)
            y = (32 - text_h) / 2 + random.randint(-2, 2) - bbox[1] # offset adjustment
            
            draw.text((x, y), cls, font=font, fill=text_color)
            
            # 3. Add augmentations (Rotation, Scaling, Noise, Blur)
            # Rotation
            angle = random.uniform(-15, 15)
            img = img.rotate(angle, resample=Image.BILINEAR, fillcolor=bg_color)
            
            # Resize
            scale = random.uniform(0.8, 1.2)
            new_size = (int(32 * scale), int(32 * scale))
            img = img.resize(new_size, Image.BILINEAR)
            
            # Crop/Pad back to 28x28 (Final target size for Char CNN)
            left = (img.width - 28) / 2
            top = (img.height - 28) / 2
            img = img.crop((left, top, left + 28, top + 28))
            
            # Add Noise
            img_arr = np.array(img)
            noise = np.random.normal(0, random.uniform(5, 15), img_arr.shape)
            img_arr = np.clip(img_arr + noise, 0, 255).astype(np.uint8)
            img = Image.fromarray(img_arr)
            
            # Blur
            if random.random() > 0.5:
                img = img.filter(ImageFilter.GaussianBlur(radius=random.uniform(0.5, 1.5)))
                
            # Save
            img.save(output_dir / cls / f"{cls}_{i}.png")
            generated_count += 1
            
    print(f"Dataset generation complete! Generated {generated_count} character images.")

def main():
    base_dir = Path(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    output_dir = base_dir / "data" / "characters"
    
    generate_synthetic_characters(output_dir, num_samples_per_class=300)

if __name__ == "__main__":
    main()
