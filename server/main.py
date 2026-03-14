from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import tempfile
import os
import sys
from datetime import datetime, timezone

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.pipeline import ANPRPipeline

app = FastAPI(title="ANPR API", description="API for the Automatic Number Plate Recognition system")

APP_VERSION = "0.2.0"
STARTED_AT = datetime.now(timezone.utc).isoformat()


def _parse_cors_origins() -> list[str]:
    raw_origins = os.getenv("ANPR_CORS_ORIGINS", "http://localhost:5173")
    origins = [origin.strip() for origin in raw_origins.split(",") if origin.strip()]
    return origins or ["http://localhost:5173"]


allowed_origins = _parse_cors_origins()

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

print("Initializing pipeline...")
try:
    pipeline = ANPRPipeline()
    pipeline_init_error = None
    print("Pipeline initialized successfully.")
except Exception as e:
    print(f"Error initializing pipeline: {e}")
    pipeline = None
    pipeline_init_error = str(e)

@app.get("/")
def read_root():
    return {"status": "ok", "message": "ANPR API is running"}


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": "anpr-api",
        "version": APP_VERSION,
        "started_at": STARTED_AT,
    }


@app.get("/ready")
def readiness_check():
    if not pipeline:
        return {
            "status": "not_ready",
            "pipeline_initialized": False,
            "error": pipeline_init_error,
        }
    return {"status": "ready", "pipeline_initialized": True}


@app.get("/version")
def version_info():
    return {"version": APP_VERSION}

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
            
        result = pipeline.process_image(tmp_path)
        
        os.unlink(tmp_path)
        
        return result
        
    except Exception as e:
        if 'tmp_path' in locals() and os.path.exists(tmp_path):
            os.unlink(tmp_path)
        raise HTTPException(status_code=500, detail=f"Error processing image: {str(e)}")
