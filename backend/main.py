
from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import shutil
import os
from pathlib import Path
from datetime import datetime
import uuid
import time

from database import Database
from config import (
    UPLOAD_DIR, OUTPUT_DIR, AVAILABLE_STYLES, 
    ALLOWED_EXTENSIONS, MAX_FILE_SIZE
)

app = FastAPI(
    title="mimicryML | AI Style Transfer API",
    description="Transform images with artistic styles using deep learning",
    version="1.0.0"
)

# Enable CORS for Streamlit frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify Streamlit URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define paths
BASE_DIR = Path(__file__).resolve().parent.parent
UPLOAD_DIR = BASE_DIR / "uploads"
OUTPUT_DIR = BASE_DIR / "outputs"

# Create directories if they don't exist
UPLOAD_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "AI Style Transfer API",
        "status": "running",
        "endpoints": {
            "health": "/health",
            "transform": "/transform",
            "status": "/status/{job_id}",
            "result": "/result/{job_id}",
            "history": "/history"
        }
    }

# Health check
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }

# Test endpoint
@app.get("/test")
async def test():
    return {"message": "Backend is working!"}

# Pydantic models for requests/responses
class TransformRequest(BaseModel):
    style: str
    session_id: str = None

class TransformResponse(BaseModel):
    job_id: str
    status: str
    message: str

class JobStatus(BaseModel):
    job_id: str
    status: str
    style_name: str
    created_at: str
    completed_at: str = None
    processing_time: float = None
    output_path: str = None
    error_message: str = None

# Helper functions
def validate_image(file: UploadFile) -> bool:
    """Validate uploaded image"""
    # Check extension
    ext = Path(file.filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed: {ALLOWED_EXTENSIONS}"
        )
    return True

async def save_upload(file: UploadFile) -> Path:
    """Save uploaded file"""
    # Generate unique filename
    ext = Path(file.filename).suffix
    unique_name = f"{uuid.uuid4()}{ext}"
    file_path = UPLOAD_DIR / unique_name
    
    # Save file
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    return file_path

# Endpoints

@app.get("/styles")
async def get_styles():
    """Get available artistic styles"""
    return {
        "styles": AVAILABLE_STYLES,
        "count": len(AVAILABLE_STYLES)
    }

@app.post("/transform", response_model=TransformResponse)
async def transform_image(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    style: str = "vangogh",
    session_id: str = None
):
    """
    Upload image and start style transfer
    Returns job_id for tracking progress
    """
    
    # Validate style
    if style not in AVAILABLE_STYLES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid style. Choose from: {list(AVAILABLE_STYLES.keys())}"
        )
    
    # Validate image
    validate_image(file)
    
    # Generate job ID
    job_id = str(uuid.uuid4())
    
    # Generate session ID if not provided
    if not session_id:
        session_id = str(uuid.uuid4())
    
    try:
        # Save uploaded file
        file_path = await save_upload(file)
        
        # Create database entry
        await Database.create_job(
            job_id=job_id,
            session_id=session_id,
            filename=file.filename,
            filepath=str(file_path),
            style=style
        )
        
        # Add processing to background tasks
        # (We'll implement the actual processing in next step)
        background_tasks.add_task(process_style_transfer, job_id, str(file_path), style)
        
        return TransformResponse(
            job_id=job_id,
            status="pending",
            message="Image uploaded successfully. Processing started."
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/status/{job_id}", response_model=JobStatus)
async def get_job_status(job_id: str):
    """Get status of a transformation job"""
    job = await Database.get_job(job_id)
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return JobStatus(**job)

@app.get("/result/{job_id}")
async def get_result(job_id: str):
    """Download the stylized image"""
    job = await Database.get_job(job_id)
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    if job['status'] != 'completed':
        raise HTTPException(
            status_code=400,
            detail=f"Job not completed. Current status: {job['status']}"
        )
    
    output_path = Path(job['output_path'])
    if not output_path.exists():
        raise HTTPException(status_code=404, detail="Result file not found")
    
    return FileResponse(
        output_path,
        media_type="image/jpeg",
        filename=f"stylized_{job_id}.jpg"
    )

@app.get("/history/{session_id}")
async def get_history(session_id: str):
    """Get transformation history for a session"""
    history = await Database.get_session_history(session_id)
    return {
        "session_id": session_id,
        "count": len(history),
        "transformations": history
    }

@app.get("/gallery")
async def get_gallery(limit: int = 20):
    """Get recent completed transformations"""
    transformations = await Database.get_all_transformations(limit)
    return {
        "count": len(transformations),
        "transformations": transformations
    }

# Placeholder for style transfer (we'll implement this next)
async def process_style_transfer(job_id: str, image_path: str, style: str):
    """
    Process style transfer (placeholder for now)
    This will be replaced with actual ML code
    """
    try:
        # Update status to processing
        await Database.update_job_status(job_id, "processing")
        
        # Simulate processing time
        start_time = time.time()
        await asyncio.sleep(5)  # Placeholder - remove when we add real processing
        processing_time = time.time() - start_time
        
        # For now, just copy the original image as output
        output_path = OUTPUT_DIR / f"{job_id}.jpg"
        shutil.copy(image_path, output_path)
        
        # Update status to completed
        await Database.update_job_status(
            job_id=job_id,
            status="completed",
            output_path=str(output_path),
            processing_time=processing_time
        )
        
    except Exception as e:
        await Database.update_job_status(
            job_id=job_id,
            status="failed",
            error_message=str(e)
        )

# Add at top with other imports
import asyncio