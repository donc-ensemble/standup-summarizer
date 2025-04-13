from celery import Celery
import os

# Get Redis URL from environment variable or use default
redis_url = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')

# Create Celery app
celery_app = Celery(
    'transcribe_summarizer',
    broker=redis_url,
    backend=redis_url
)

celery_app.autodiscover_tasks(['backend.services'])

# Optional configurations
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
)