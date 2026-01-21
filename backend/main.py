
from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import shutil
import os
import asyncio
from pathlib import Path
from datetime import datetime
import uuid
import time
from style_transfer import StyleTransfer
from config import MODEL_DIR
from typing import Optional
from pydantic import BaseModel

from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path

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

def load_template(template_name: str) -> str:
    """Load HTML template from file"""
    template_path = Path(__file__).parent / "templates" / template_name
    with open(template_path, 'r', encoding='utf-8') as f:
        return f.read()

# Root endpoint
@app.get("/", response_class=HTMLResponse)
# @app.get("/")
async def root():
    """Serve the landing page"""
    return load_template("index.html")
    # return {
    #     "message": "mimicryML | AI Style Transfer API",
    #     "status": "running",
    #     "endpoints": {
    #         "health": "/health",
    #         "transform": "/transform",
    #         "status": "/status/{job_id}",
    #         "result": "/result/{job_id}",
    #         "history": "/history"
    #     }
    # }

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
    session_id: Optional[str] = None

class TransformResponse(BaseModel):
    job_id: str
    status: str
    message: str

class JobStatus(BaseModel):
    job_id: str
    status: str
    style_name: str
    created_at: str
    completed_at: Optional[str] = None
    processing_time: Optional[float] = None
    output_path: Optional[str] = None
    error_message: Optional[str] = None

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

@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the landing page"""
    return load_template("index.html")

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

async def process_style_transfer(job_id: str, image_path: str, style: str):
    """
    Process style transfer with actual ML model
    """
    try:
        print(f"\n{'='*60}")
        print(f"🎨 Starting style transfer for job: {job_id}")
        print(f"   Style: {style}")
        print(f"{'='*60}\n")
        
        # Update status to processing
        await Database.update_job_status(job_id, "processing")
        
        # Get style image path
        style_dir = Path(__file__).resolve().parent.parent / "models" / "style_images"
        style_path = style_dir / f"{style}.jpg"
        
        if not style_path.exists():
            raise FileNotFoundError(f"Style image not found: {style}.jpg")
        
        # Output path
        output_path = OUTPUT_DIR / f"{job_id}.jpg"
        
        # Create style transfer instance and apply
        start_time = time.time()
        st = StyleTransfer(max_dim=512)
        result = st.apply_style(
            content_path=Path(image_path),
            style_path=style_path,
            output_path=output_path
        )
        processing_time = time.time() - start_time
        
        if result["success"]:
            # Update database with success
            await Database.update_job_status(
                job_id=job_id,
                status="completed",
                output_path=str(output_path),
                processing_time=processing_time
            )
            print(f"\n✅ Job {job_id} completed successfully!\n")
        else:
            # Update database with failure
            await Database.update_job_status(
                job_id=job_id,
                status="failed",
                error_message=result.get("error", "Unknown error")
            )
            print(f"\n❌ Job {job_id} failed!\n")
        
    except Exception as e:
        print(f"\n❌ Error processing job {job_id}: {str(e)}\n")
        await Database.update_job_status(
            job_id=job_id,
            status="failed",
            error_message=str(e)
        ) 

def load_template(template_name: str) -> str:
    """Load HTML template from file"""
    template_path = Path(__file__).parent / "templates" / template_name
    with open(template_path, 'r', encoding='utf-8') as f:
        return f.read()