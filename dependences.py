from typing import Literal

from fastapi import HTTPException

from service.download_abstract_service import DownloadAbstractService
from service.download_service import DownloadPytubefixService, DownloadYtDlpService


def get_download_service() -> DownloadPytubefixService:
    return DownloadPytubefixService()

def get_download_ytdlp_service() -> DownloadYtDlpService:
    return DownloadYtDlpService()

def get_service(service_name: Literal["pytubefix", "yt-dlp"]) -> DownloadAbstractService:
    services = {
        "pytubefix": DownloadPytubefixService,
        "yt-dlp": DownloadYtDlpService,
    }

    service = services.get(service_name)
    if not service:
        raise HTTPException(status_code=402, detail="Service not found")
    return service()