# Audio Summarizer Full Stack Project

A full-stack application that transcribes audio files using Whisper AI, summarizes the text using Anthropic's API, and stores the results in PostgreSQL. Built with FastAPI (Python) backend and Vue.js frontend, containerized with Docker.

## Features

- 🎤 Upload recording files (WAV, MP4)
- 🔍 Automatic transcription using Whisper AI
- 📝 AI-powered summarization using Anthropic API
- 💾 Persistent storage in PostgreSQL (projects, channels, summaries)
- 🏗️ Database migrations with Alembic
- 🔔 Slack notifications for completed summaries
- ⚡ Background processing with FastAPI's BackgroundTasks
- 🐳 Dockerized for easy development and deployment

## Tech Stack

**Backend:**
- Python
- FastAPI (REST API)
- SQLAlchemy (ORM)
- Alembic (database migrations)
- PostgreSQL (database)
- Whisper AI (audio transcription)
- Anthropic API (text summarization)
- Docker

**Frontend:**
- Vue.js 3
- Vue-Toastification (notifications)
- EventSource (SSE for real-time updates)
- Docker

## Prerequisites

- Docker and Docker Compose
- Anthropic API Key
- (Optional) Slack Bot Token and Channel ID for notifications

## Getting Started

1. Clone the repository:
   ```bash
   git clone https://github.com/your-repo/audio-summarizer.git
   cd audio-summarizer
2. Create a .env file in the root directory with required environment variables:
    ```bash
    ANTHROPIC_API_KEY=your_anthropic_api_key
    WHISPER_MODEL=base  # or small, medium, large
    # Optional Slack integration
    SLACK_BOT_TOKEN=your_slack_bot_token
3. Run the application:
    ```bash
    chmod +x run.sh  # Make the script executable if needed
    ./run.sh

## Access the Applications (Development)
* Frontend: http://localhost:8080
* Backend API: http://localhost:8000
* API Docs (Swagger UI): http://localhost:8000/docs

## Database Migrations with Alembic
The project uses Alembic for database schema migrations. To create and apply migrations:
1. Enter the backend container:
    ```bash
    docker compose exec backend bash

2. Create a new migration:
    ```bash
    alembic revision --autogenerate -m "Your migration message"

3. Apply migrations
    ```bash
    alembic upgrade head
4. To reset the database (strictly for development only):
    ```bash
    alembic downgrade base && alembic upgrade head
Migration files are stored in backend/alembic/versions/

## Project Structure
```bash
├── backend/                 # FastAPI backend
│   ├── alembic/             # Alembic migration files
│   │   ├── versions/        # Generated migration scripts
│   │   ├── env.py           # Migration environment
│   │   └── script.py.mako   # Migration template
│   ├── api/                 # API routes
│   ├── db/                  # Database models, schemas, and sessions
│   ├── services/            # Business logic (transcription, summarization)
│   ├── alembic.ini          # Alembic configuration
│   └── main.py              # FastAPI application entry point
├── frontend/                # Vue.js frontend
│   ├── src/                 # Vue components, routes and logic
│   └── package.json         # Frontend dependencies
├── docker-compose.yml       # Docker compose configuration
├── Dockerfile               # Docker configuration
├── run.sh                   # Convenience script
└── .env.example             # Environment variables template
```


## API Endpoints
Key endpoints:

* POST /upload-audio/ - Upload an audio file for processing
* GET /job-events/{job_id} - SSE stream for job status updates
* GET /projects/ - List all projects
* GET /channels/ - List all channels
* GET /summaries/ - List all summaries

See full API documentation at http://localhost:8000/docs when running locally.

## Background processing
The system uses FastAPI's BackgroundTasks to handle long-running operations (transcription + summarization) without blocking the API. This allows:
* Immediate response to the user
* Real-time status updates via Server-Sent Events (SSE)
* Ability to continue making other API calls during processing

## Future Improvements
1. Replace BackgroundTasks with Redis + Celery for better scalability
2. Zoom Marketplace and Teams integration
3. Confluence integration for saving summaries
4. Action item extraction
5. Sentiment analysis