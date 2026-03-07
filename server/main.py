from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import tempfile
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.pipeline import ANPRPipeline

app = FastAPI(title="ANPR API", description="API for the Automatic Number Plate Recognition system")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

print("Initializing pipeline...")
try:
    # Load pipeline
    pipeline = ANPRPipeline()
    print("Pipeline initialized successfully.")
except Exception as e:
    print(f"Error initializing pipeline: {e}")
    pipeline = None

@app.get("/")
def read_root():
    return {"status": "ok", "message": "ANPR API is running"}

@app.post("/api/verify")
async def verify_plate(file: UploadFile = File(...)):
    if not pipeline:
        raise HTTPException(status_code=500, detail="ANPR Pipeline is not initialized")
        
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")
        
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp_file:
            content = await file.read()
            tmp_file.write(content)
            tmp_path = tmp_file.name
            
        # Call the actual ML pipeline
        result = pipeline.process_image(tmp_path)
        
        # Cleanup
        os.unlink(tmp_path)
        
        # Even if pipeline returns status error (e.g. no plate detected), we return it properly
        return result
        
    except Exception as e:
        if 'tmp_path' in locals() and os.path.exists(tmp_path):
            os.unlink(tmp_path)
        raise HTTPException(status_code=500, detail=f"Error processing image: {str(e)}")
