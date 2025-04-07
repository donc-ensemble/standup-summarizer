import subprocess
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

from fastapi.middleware.cors import CORSMiddleware

from api.routes.projects import router as projects_router
from api.routes.channels import router as channels_router
from api.routes.summaries import router as summaries_router

sys.path.append(str(Path(__file__).parent))
from services.transcribe_summarizer import transcribe_summarize_api


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print(f"Tables created: {list(Base.metadata.tables.keys())}")
    
    yield
    
    print("Shutting down...")
    
app = FastAPI(lifespan=lifespan)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(projects_router, prefix="/projects", tags=["projects"])
app.include_router(channels_router, prefix="/channels", tags=["channels"])
app.include_router(summaries_router, prefix="/summaries", tags=["summaries"])

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.post("/upload-audio/")
async def upload_audio(background_tasks: BackgroundTasks, channel_id: int, audio_file: UploadFile = File(...)):
    """
    Endpoint to upload an audio file and process it using the transcribe_summarize function.
    Accepts audio files including MP4 and M4A formats, converting them to WAV as needed.
    
    Args:
        background_tasks: FastAPI background tasks handler
        channel_id: The ID of the channel to associate with this upload
        audio_file: The uploaded audio file
    
    Returns:
        JSONResponse with job_id and status
    """
    # Accept audio files and video files (for MP4)
    content_type = audio_file.content_type
    if not (content_type.startswith("audio/") or content_type.startswith("video/")):
        raise HTTPException(status_code=400, detail="File must be an audio or video file")
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    job_id = f"standup_{timestamp}_{uuid.uuid4().hex[:8]}"
    
    # Create temporary directory for processing
    temp_dir = os.getenv("TEMP_DIRECTORY", "/tmp/audio_processing")
    os.makedirs(temp_dir, exist_ok=True)
    
    # Save original file temporarily
    file_extension = os.path.splitext(audio_file.filename)[1].lower()
    if not file_extension:
        file_extension = ".wav"  # Default to .wav if no extension
    
    original_filename = audio_file.filename
    temp_file_path = os.path.join(temp_dir, f"{job_id}_original{file_extension}")
    
    with open(temp_file_path, "wb") as buffer:
        shutil.copyfileobj(audio_file.file, buffer)
    
    if file_extension in ['.mp4', '.m4a']:
        wav_file_path = os.path.join(temp_dir, f"{job_id}_recording.wav")
        try:
            subprocess.run(
                ["ffmpeg", "-i", temp_file_path, "-vn", "-acodec", "pcm_s16le", "-ar", "44100", "-ac", "2", wav_file_path],
                check=True
            )
            audio_file_path = wav_file_path
        except subprocess.CalledProcessError as e:
            raise HTTPException(status_code=500, detail=f"Failed to convert audio: {str(e)}")
    else:
        audio_file_path = temp_file_path
    
    background_tasks.add_task(
        transcribe_summarize_api,
        audio_file_path=audio_file_path,
        channel_id=channel_id,
        original_filename=original_filename
    )
    
    return JSONResponse(
        status_code=202,
        content={
            "job_id": job_id,
            "status": "processing",
            "message": "Audio file uploaded successfully. Processing started."
        }
    )

@app.get("/job-status/{job_id}")
async def get_job_status(job_id: str):
    """
    Enhanced endpoint to check the status of a processing job
    
    Args:
        job_id: The job identifier
        
    Returns:
        JSONResponse with job status and available data
    """
    db = next(get_db())
    try:
        from db.models.summary import Summary
        summary = db.query(Summary).filter(Summary.job_id == job_id).first()
        
        if not summary:
            return JSONResponse(
                status_code=404,
                content={
                    "job_id": job_id,
                    "status": "not_found",
                    "message": "Job not found in database"
                }
            )
        
        # More detailed status checking
        if summary.error_message:
            status = "failed"
        elif summary.transcript and summary.summary:
            status = "completed"
        elif summary.transcript:
            status = "transcribed"  # Optional intermediate state
        else:
            status = "processing"
        
        available_data = {
            "transcript": bool(summary.transcript),
            "summary": bool(summary.summary)
        }
        
        response = {
            "job_id": job_id,
            "status": status,
            "summary_id": summary.id,
            "available_data": available_data
        }
        
        if summary.error_message:
            response["error"] = summary.error_message
            
        return JSONResponse(content=response)
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "job_id": job_id,
                "status": "error",
                "message": f"Error checking job status: {str(e)}"
            }
        )
    finally:
        db.close()

def main():
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    main()