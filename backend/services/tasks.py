import time
from .celery_app import celery_app


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