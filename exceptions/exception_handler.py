from urllib.error import URLError

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from pytubefix.exceptions import VideoUnavailable
from starlette.responses import JSONResponse
from yt_dlp import DownloadError


def register_exception_handler(app: FastAPI):
    @app.exception_handler(DownloadError)
    async def download_ytdlp_exception_handler(request: Request, exc: DownloadError):
        return JSONResponse(
            status_code=402,
            content={"detail": "Something went wrong, please try another resolution or try another service"},
        )

    @app.exception_handler(VideoUnavailable)
    async def age_exception_handler(request: Request, exc: VideoUnavailable):
        return JSONResponse(
            status_code=403,
            content={"detail": exc.error_string},
        )

    @app.exception_handler(URLError)
    async def url_exception_handler(request: Request, exc: URLError):
        return JSONResponse(
            status_code=500,
            content={"detail": "Host dont respond"},
        )

