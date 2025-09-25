from typing import List

from fastapi import APIRouter
from fastapi.params import Depends

from starlette.responses import FileResponse

from dependences import get_service
from filter.video_filter import FilterParams, BaseFilter, ResolutionFilter
from schema.stream_schema import StreamSchema
from service.download_abstract_service import DownloadAbstractService

router = APIRouter(
    prefix="/loader",
    tags=["loader"],
)


@router.get("/all")
async def get_streams_info(video_url: str, filter_query: BaseFilter = Depends(FilterParams), download_service: DownloadAbstractService = Depends(get_service)) -> List[StreamSchema]:
    result = await download_service.get_video_info(video_url, filter_query)
    return result

@router.get("/fastest")
async def get_fastest_stream(video_url: str, download_service: DownloadAbstractService = Depends(get_service)) -> List[StreamSchema]:
    result = await download_service.get_fastest_video(video_url=video_url)
    return result

@router.get("/download")
async def download_video(video_url: str, filter_query: BaseFilter = Depends(ResolutionFilter), download_service: DownloadAbstractService = Depends(get_service)) -> FileResponse:
    result = await download_service.download_video(video_url=video_url, filter_query=filter_query)
    print(result)
    return result
