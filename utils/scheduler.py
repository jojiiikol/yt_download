from datetime import datetime, timedelta

from apscheduler.executors.pool import ThreadPoolExecutor, ProcessPoolExecutor
from apscheduler.jobstores.memory import MemoryJobStore
import os

from apscheduler.schedulers.background import BackgroundScheduler

from settings import POSIX_MEDIA_DIR

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


def cleanup_task() -> None:
    dir_path = POSIX_MEDIA_DIR
    files = os.listdir(dir_path)
    for file in files:
        file_datetime_created = datetime.strptime(file.split(".")[0], "%Y%m%d-%H%M%S")
        if datetime.now() - file_datetime_created > timedelta(hours=1):
            print(f"Deleting {file}")
            os.remove(os.path.join(dir_path, file))

scheduler.add_job(cleanup_task, "interval", minutes=60)