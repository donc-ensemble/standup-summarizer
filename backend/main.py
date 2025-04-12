import asyncio
import json
import subprocess
from fastapi import FastAPI, Form, Request, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse, StreamingResponse
import os
import uuid
from datetime import datetime
import shutil
import sys
from pathlib import Path
from contextlib import asynccontextmanager
from db.models.summary import Summary
from db.base import Base
from db.session import engine, get_db

from fastapi.middleware.cors import CORSMiddleware

from api.routes.projects import router as projects_router
from api.routes.channels import router as channels_router
from api.routes.summaries import router as summaries_router


sys.path.append(str(Path(__file__).parent))
from services.transcribe_summarizer import transcribe_summarize_api
from services.tasks import sleep_task


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
    expose_headers=["*"],
)


app.include_router(projects_router, prefix="/projects", tags=["projects"])
app.include_router(channels_router, prefix="/channels", tags=["channels"])
app.include_router(summaries_router, prefix="/summaries", tags=["summaries"])


@app.get("/")
def read_root():
    return {"Hello": "Welcome to Summarizer! Feel free to summarize any recordings"}
  
  
# Start of Celery
@app.get("/trigger-sleep-task/{seconds}")
async def trigger_sleep_task(seconds: int):
    """
    Endpoint to trigger a sleep task with Celery
    """
    task = sleep_task.delay(seconds)
    return {"message": f"Sleep task started for {seconds} seconds", "task_id": task.id}

@app.get("/check-task/{task_id}")
async def check_task(task_id: str):
    """
    Endpoint to check the status of a task
    """
    task = sleep_task.AsyncResult(task_id)
    if task.ready():
        return {"status": "completed", "result": task.result}
    return {"status": "in progress"}
# End of Celery


@app.post("/upload-audio/")
async def upload_audio(
    background_tasks: BackgroundTasks,
    channel_id: int,
    audio_file: UploadFile = File(...),
    send_to_slack: str = Form("true"),
):
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
        raise HTTPException(
            status_code=400, detail="File must be an audio or video file"
        )

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

    if file_extension in [".mp4", ".m4a"]:
        wav_file_path = os.path.join(temp_dir, f"{job_id}_recording.wav")
        try:
            subprocess.run(
                [
                    "ffmpeg",
                    "-i",
                    temp_file_path,
                    "-vn",
                    "-acodec",
                    "pcm_s16le",
                    "-ar",
                    "44100",
                    "-ac",
                    "2",
                    wav_file_path,
                ],
                check=True,
            )
            audio_file_path = wav_file_path
        except subprocess.CalledProcessError as e:
            raise HTTPException(
                status_code=500, detail=f"Failed to convert audio: {str(e)}"
            )
    else:
        audio_file_path = temp_file_path

    db = next(get_db())
    try:
        db_summary = Summary(
            job_id=job_id,
            channel_id=channel_id,
            original_filename=original_filename,
            slack_notification_sent=False, 
            status="pending",
        )
        db.add(db_summary)
        db.commit()
        db.refresh(db_summary)
    finally:
        db.close()

    background_tasks.add_task(
        transcribe_summarize_api,
        audio_file_path=audio_file_path,
        channel_id=channel_id,
        original_filename=original_filename,
        job_id=job_id,
        send_to_slack_bool=send_to_slack.lower() == "true"
    )

    return JSONResponse(
        status_code=202,
        content={
            "job_id": job_id,
            "status": "pending",
            "message": "Audio file uploaded successfully. Processing started.",
        },
    )


@app.get("/job-events/{job_id}")
async def job_events(request: Request, job_id: str):
    async def event_generator():
        while True:
            if await request.is_disconnected():
                print(f"Client disconnected for job {job_id}")
                break

            db = next(get_db())  
            try:
                summary = db.query(Summary).filter(Summary.job_id == job_id).first()
                if not summary:
                    yield f"data: {json.dumps({'error': 'Job not found'})}\n\n"
                    break

                print(f"Current status for {job_id}: {summary.status}")

                if summary.status == "completed":
                    payload = json.dumps({
                        'status': 'completed',
                        'message': 'Processing complete',
                        'summary_id': summary.id,
                        'slack_notification_sent': summary.slack_notification_sent,
                        'slack_error': getattr(summary, 'slack_error', None)
                    })
                    yield f"data: {payload}\n\n"
                    break
                elif summary.status == "failed":
                    payload = json.dumps({
                        'status': 'failed',
                        'error': getattr(summary, 'error', 'Unknown error')
                    })
                    yield f"data: {payload}\n\n"
                    break
                else:
                    payload = json.dumps({
                        'status': summary.status,
                        'message': f'Current status: {summary.status}'
                    })
                    yield f"data: {payload}\n\n"
            finally:
                db.close() 

            await asyncio.sleep(2)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # Important for Nginx/proxies
        },
    )


def main():
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()
