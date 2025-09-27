from typing import Literal

from fastapi import HTTPException

from service.combine_abstract_service import CombineAbstractService
from service.combine_service import CombineFfmpegService
from service.cookie_abstract_service import CookieAbstractService
from service.cookie_service import CookieService
from service.download_abstract_service import DownloadAbstractService
from service.download_service import DownloadPytubefixService, DownloadYtDlpService
from service.proxy_abstract_service import ProxyAbstractService
from service.proxy_service import ProxyService


def get_combine_service() -> CombineAbstractService:
    return CombineFfmpegService()

def get_download_pytubefix_service() -> DownloadPytubefixService:
    return DownloadPytubefixService(get_combine_service())

def get_download_ytdlp_service() -> DownloadYtDlpService:
    return DownloadYtDlpService(get_combine_service())

def get_cookie_service() -> CookieAbstractService:
    return CookieService()

def get_proxy_service() -> ProxyAbstractService:
    return ProxyService()


def get_service(service_name: Literal["pytubefix", "yt-dlp"]) -> DownloadAbstractService:
    services = {
        "pytubefix": get_download_pytubefix_service,
        "yt-dlp": get_download_ytdlp_service,
    }

    service = services.get(service_name)
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    return service()