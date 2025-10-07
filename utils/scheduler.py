from datetime import datetime, timedelta

from apscheduler.executors.asyncio import AsyncIOExecutor
from apscheduler.executors.pool import ThreadPoolExecutor, ProcessPoolExecutor
from apscheduler.jobstores.memory import MemoryJobStore
import os

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.schedulers.background import BackgroundScheduler
from fastapi import Depends

from dependences import get_cookie_service, get_proxy_service
from service.cookie_abstract_service import CookieAbstractService
from service.proxy_abstract_service import ProxyAbstractService
from settings import POSIX_MEDIA_DIR, COOKIES_DIR

jobstores = {
    "default": MemoryJobStore()
}

executors = {
    "default": AsyncIOExecutor()
}

job_defaults = {
    "coalesce": True,
    "max_instances": 1
}

scheduler = AsyncIOScheduler(jobstores=jobstores, executors=executors, job_defaults=job_defaults)

async def clean_dir(path: str):
    files = os.listdir(path)
    for file in files:
        if file == "cookie.txt":
            continue
        file_datetime_created = datetime.strptime(file.split(".")[0], "%Y%m%d-%H%M%S-%f")
        if datetime.now() - file_datetime_created > timedelta(hours=1):
            print(f"Deleting {file}")
            os.remove(os.path.join(path, file))


async def cleanup_task() -> None:
    await clean_dir(COOKIES_DIR)
    await clean_dir(POSIX_MEDIA_DIR)

async def refresh_cookie_task(cookie_service: CookieAbstractService = get_cookie_service(), proxy_service : ProxyAbstractService = get_proxy_service()) -> None:
    cookie_path = os.path.join(COOKIES_DIR, "cookie.txt")
    proxy = await proxy_service.get_proxy()
    print(proxy)
    cookie_path = await cookie_service.refresh_cookie_2(proxy_url=proxy, cookie_path=cookie_path)
    print(f"Refreshed cookie: {cookie_path}")

scheduler.add_job(cleanup_task, "interval", minutes=60)
scheduler.add_job(refresh_cookie_task, "interval", minutes=2)