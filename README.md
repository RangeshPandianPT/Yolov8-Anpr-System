# Deep Learning Based Vehicle Number Plate Verification System

This repository contains the codebase for the Next-Generation ANPR system.

## Project Structure
- `src/`: Core Python ML Pipeline (Detection, Segmentation, Recognition, Verification)
- `server/`: Asynchronous **FastAPI Backend** serving the ML Models
- `frontend/`: Premium, glassmorphism-inspired **React Vite Frontend**

## Setup Instructions

### 1. Backend (FastAPI)
```bash
# Create and activate virtual environment
python -m venv venv
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start the Backend Server (runs on Port 8000)
python -m uvicorn server.main:app --host 0.0.0.0 --port 8000
```

### 2. Frontend (Vite React)
```bash
# Navigate to the frontend directory
cd frontend

# Install Node dependencies
npm install

# Start the Frontend Dev Server (runs on Port 5173)
npm run dev
```

Open your browser to `http://localhost:5173` and upload a vehicle image to test the visually stunning ANPR verification interface!
