import os
from contextlib import asynccontextmanager

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI
from router.downloader_router import router as downloader_router
from utils.scheduler import scheduler

load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    scheduler.start()
    print("Scheduler started")
    yield
    scheduler.shutdown()
    print("Scheduler stopped")
app = FastAPI(title="yt-download_client", lifespan=lifespan)
app.include_router(downloader_router)



if __name__ == "__main__":
    uvicorn.run(app, host=os.getenv("APP_HOST"), port=int(os.getenv("APP_PORT")))