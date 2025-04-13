import time
from .celery_app import celery_app
from .transcribe_summarizer import transcribe_summarize_api


@celery_app.task(name="sleep_task")
def sleep_task(seconds):
    """
    A simple task that sleeps for the specified number of seconds
    and returns a message indicating it has completed.
    """
    time.sleep(seconds)
    return f"Slept for {seconds} seconds"


@celery_app.task(name="add_numbers")
def add_numbers(x, y):
    """
    A simple task that adds two numbers.
    """
    return x + y


@celery_app.task(name="transcribe_and_summarize_task")
def transcribe_and_summarize_task(audio_file_path, channel_id, original_filename, job_id, send_to_slack_bool):
    try:
        transcribe_summarize_api(
            audio_file_path=audio_file_path,
            channel_id=channel_id,
            original_filename=original_filename,
            job_id=job_id,
            send_to_slack_bool=send_to_slack_bool,
        )
    except Exception as e:
        from celery import current_task
        current_task.retry(exc=e, countdown=10, max_retries=3)