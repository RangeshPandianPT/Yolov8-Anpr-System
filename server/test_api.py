import requests
import os
import glob

def test_pipeline():
    img_path = r"D:\Num_Plate\State-wise_OLX\MH\MH1.jpg"
    if not os.path.exists(img_path):
        print(f"No test image found directly at {img_path}")
        return
        for root, dirs, files in os.walk(base_dir):
            if 'venv' in root or 'node_modules' in root:
                continue
            for f in files:
                if f.lower().endswith(('.jpg', '.jpeg', '.png')):
                    img_path = os.path.join(root, f)
                    break
            if img_path:
                break
                
    if not img_path:
        print("No test image found.")
        return
        
    print(f"Testing API with image: {img_path}")
    url = "http://localhost:8000/api/verify"
    
    with open(img_path, 'rb') as f:
        files = {'file': (os.path.basename(img_path), f, 'image/jpeg')}
        try:
            response = requests.post(url, files=files)
            print(f"Status Code: {response.status_code}")
            print(f"Response: {response.json()}")
        except Exception as e:
            print(f"Error connecting to server: {e}")

if __name__ == "__main__":
    test_pipeline()
