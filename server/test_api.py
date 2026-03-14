import requests
import os


def find_first_image(base_dir):
    for root, _, files in os.walk(base_dir):
        if 'venv' in root or 'node_modules' in root:
            continue
        for f in files:
            if f.lower().endswith(('.jpg', '.jpeg', '.png')):
                return os.path.join(root, f)
    return None

def test_pipeline():
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    img_path = os.getenv("ANPR_TEST_IMAGE", r"D:\Num_Plate\State-wise_OLX\MH\MH1.jpg")

    if not os.path.exists(img_path):
        print(f"No test image found at {img_path}. Searching in repo...")
        img_path = find_first_image(base_dir)

    if not img_path:
        print("No test image found.")
        return

    print(f"Testing API with image: {img_path}")
    api_url = os.getenv("ANPR_TEST_API_URL", "http://localhost:8000/api/verify")
    
    with open(img_path, 'rb') as f:
        files = {'file': (os.path.basename(img_path), f, 'image/jpeg')}
        try:
            response = requests.post(api_url, files=files)
            print(f"Status Code: {response.status_code}")
            print(f"Response: {response.json()}")
        except Exception as e:
            print(f"Error connecting to server: {e}")

if __name__ == "__main__":
    test_pipeline()
