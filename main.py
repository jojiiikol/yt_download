import os

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI
from router.downloader_router import router as downloader_router

load_dotenv()

app = FastAPI(title="yt-download_client")
app.include_router(downloader_router)

if __name__ == "__main__":
    uvicorn.run(app, host=os.getenv("APP_HOST"), port=int(os.getenv("APP_PORT")))