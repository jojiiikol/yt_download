import os
from contextlib import asynccontextmanager

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import RedirectResponse
from starlette.staticfiles import StaticFiles

from exceptions.exception_handler import register_exception_handler
from router.downloader_router import router as downloader_router
from router.proxy_router import router as proxy_router
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
app.mount("/static", StaticFiles(directory="./staticfiles"), name="static")

origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

register_exception_handler(app)
app.include_router(downloader_router)
app.include_router(proxy_router)





if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)