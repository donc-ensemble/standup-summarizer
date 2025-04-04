from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
import os
import uuid
from datetime import datetime
import shutil
import sys
from pathlib import Path
from contextlib import asynccontextmanager
from db.base import Base
from db.session import engine, get_db 
from typing import AsyncIterator

from api.routes.projects import router as projects_router
from api.routes.channels import router as channels_router
from api.routes.summaries import router as summaries_router

sys.path.append(str(Path(__file__).parent))
from services.transcribe_summarizer import transcribe_summarize_api

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create database tables
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print(f"Tables created: {list(Base.metadata.tables.keys())}")
    
    yield  # App runs here
    
    # Cleanup (if needed)
    print("Shutting down...")
app = FastAPI(lifespan=lifespan)

app.include_router(projects_router, prefix="/projects", tags=["projects"])
app.include_router(channels_router, prefix="/channels", tags=["channels"])
app.include_router(summaries_router, prefix="/summaries", tags=["summaries"])

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.post("/upload-audio/")
async def upload_audio(background_tasks: BackgroundTasks, audio_file: UploadFile = File(...)):
    """
    Endpoint to upload an audio file and process it using the transcribe_summarize function.
    
    Args:
        background_tasks: FastAPI background tasks handler
        audio_file: The uploaded audio file
    
    Returns:
        JSONResponse with job_id and status
    """
    content_type = audio_file.content_type
    if not content_type.startswith("audio/"):
        raise HTTPException(status_code=400, detail="File must be an audio file")
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    job_id = f"standup_{timestamp}_{uuid.uuid4().hex[:8]}"
    
    base_output_dir = os.getenv("OUTPUT_DIRECTORY", "/app/output")
    session_dir = os.path.join(base_output_dir, job_id)
    os.makedirs(session_dir, exist_ok=True)
    
    file_extension = os.path.splitext(audio_file.filename)[1]
    if not file_extension:
        file_extension = ".wav"  # Default to .wav if no extension
    
    audio_file_path = os.path.join(session_dir, f"{job_id}_recording{file_extension}")
    
    with open(audio_file_path, "wb") as buffer:
        shutil.copyfileobj(audio_file.file, buffer)
    
    background_tasks.add_task(
        transcribe_summarize_api,
        audio_file_path=audio_file_path
    )
    
    return JSONResponse(
        status_code=202,
        content={
            "job_id": job_id,
            "status": "processing",
            "message": "Audio file uploaded successfully. Processing started.",
            "session_dir": session_dir
        }
    )

@app.get("/job-status/{job_id}")
async def get_job_status(job_id: str):
    """
    Endpoint to check the status of a processing job
    
    Args:
        job_id: The job identifier
        
    Returns:
        JSONResponse with job status and available files
    """
    base_output_dir = os.getenv("OUTPUT_DIRECTORY", "/app/output")
    session_dir = os.path.join(base_output_dir, job_id)
    
    if not os.path.exists(session_dir):
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
    
    files = os.listdir(session_dir)
    transcript_file = next((f for f in files if "transcript" in f), None)
    summary_file = next((f for f in files if "summary" in f), None)
    
    status = "completed" if transcript_file and summary_file else "processing"
    
    available_files = {}
    if transcript_file:
        available_files["transcript"] = f"/output/{job_id}/{transcript_file}"
    if summary_file:
        available_files["summary"] = f"/output/{job_id}/{summary_file}"
    
    return JSONResponse(
        content={
            "job_id": job_id,
            "status": status,
            "available_files": available_files
        }
    )

def main():
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    main()