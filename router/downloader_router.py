from fastapi import APIRouter
from fastapi.params import Depends

from dependences import get_download_service, get_download_ytdlp_service
from service.download_abstract_service import DownloadAbstractService

router = APIRouter(
    prefix="/loader",
    tags=["loader"],
)

@router.get("/")
async def get_video_info(video_url: str, download_service: DownloadAbstractService = Depends(get_download_service)):
    result = await download_service.get_video_info(video_url)
    return result

@router.get("/dlp")
async def get_dlp_info(video_url: str, download_service: DownloadAbstractService = Depends(get_download_ytdlp_service)):
    result = await download_service.get_video_info(video_url)
    return result
