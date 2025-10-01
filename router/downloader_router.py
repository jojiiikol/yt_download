from typing import List

from fastapi import APIRouter, Form
from fastapi.params import Depends, Body

from starlette.responses import FileResponse

from dependences import get_service, get_cookie_service, get_proxy_service
from filter.video_filter import FilterParams, BaseFilter, ResolutionFilter
from schema.proxy_schema import ProxySchema
from schema.stream_schema import StreamSchema
from service.cookie_abstract_service import CookieAbstractService
from service.download_abstract_service import DownloadAbstractService
from service.proxy_abstract_service import ProxyAbstractService

router = APIRouter(
    prefix="/loader",
    tags=["loader"],
)


@router.post("/all")
async def get_streams_info(video_url: str, filter_query: BaseFilter = Depends(FilterParams),
                            proxy_url: None | str = None,
                           cookies_text: None | str = Body(None, media_type="text/plain"),
                           download_service: DownloadAbstractService = Depends(get_service),
                           cookie_service: CookieAbstractService = Depends(get_cookie_service),
                           proxy_service: ProxyAbstractService = Depends(get_proxy_service)) -> List[StreamSchema]:

    proxy = await proxy_service.get_proxy(proxy_url=proxy_url)
    cookie = await cookie_service.get_cookie_path(proxy_url=proxy, cookie_text=cookies_text)
    result = await download_service.get_video_info(video_url=video_url, proxy_url=proxy.url, cookie_file=cookie,
                                                   filter_query=filter_query)
    return result


@router.post("/fastest")
async def get_fastest_stream(video_url: str, proxy_url: None | str = None,
                             cookies_text: None | str = Body(None, media_type="text/plain"),
                             download_service: DownloadAbstractService = Depends(get_service),
                             cookie_service: CookieAbstractService = Depends(get_cookie_service),
                             proxy_service: ProxyAbstractService = Depends(get_proxy_service)) -> StreamSchema:

    proxy = await proxy_service.get_proxy(proxy_url=proxy_url)
    cookie = await cookie_service.get_cookie_path(proxy_url=proxy, cookie_text=cookies_text)
    result = await download_service.get_fastest_video(video_url=video_url, proxy_url=proxy.url, cookie_file=cookie)
    return result


@router.post("/download")
async def download_video(video_url: str,  proxy_url: None | str = None, filter_query: BaseFilter = Depends(ResolutionFilter),
                         cookies_text: None | str = Body(None, media_type="text/plain"),
                         download_service: DownloadAbstractService = Depends(get_service),
                         cookie_service: CookieAbstractService = Depends(get_cookie_service),
                         proxy_service: ProxyAbstractService = Depends(get_proxy_service)) -> FileResponse:


    proxy = await proxy_service.get_proxy(proxy_url=proxy_url)
    cookie = await cookie_service.get_cookie_path(proxy_url=proxy, cookie_text=cookies_text)
    result = await download_service.download_video(video_url=video_url, proxy_url=proxy.url, cookie_file=cookie, filter_query=filter_query)

    return result
