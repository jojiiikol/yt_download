from datetime import datetime, timedelta

from apscheduler.executors.pool import ThreadPoolExecutor, ProcessPoolExecutor
from apscheduler.jobstores.memory import MemoryJobStore
import os

from apscheduler.schedulers.background import BackgroundScheduler

from settings import POSIX_MEDIA_DIR, COOKIES_DIR

jobstores = {
    "default": MemoryJobStore()
}

executors = {
    "default": ThreadPoolExecutor(max_workers=3),
    "processpool": ProcessPoolExecutor(max_workers=1)
}

job_defaults = {
    "coalesce": True,
    "max_instances": 1
}

scheduler = BackgroundScheduler(jobstores=jobstores, executors=executors, job_defaults=job_defaults)

def clean_dir(path: str):
    files = os.listdir(path)
    for file in files:
        file_datetime_created = datetime.strptime(file.split(".")[0], "%Y%m%d-%H%M%S")
        if datetime.now() - file_datetime_created > timedelta(hours=1):
            print(f"Deleting {file}")
            os.remove(os.path.join(path, file))

def cleanup_task() -> None:
    clean_dir(COOKIES_DIR)
    clean_dir(POSIX_MEDIA_DIR)

scheduler.add_job(cleanup_task, "interval", minutes=60)