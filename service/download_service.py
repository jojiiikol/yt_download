import socket
import time
from datetime import datetime
import random
from typing import Dict, List

from fastapi import HTTPException
from starlette.responses import FileResponse
from yt_dlp import YoutubeDL

from filter.video_filter import FilterParams, ResolutionFilter
import asyncio

from schema.proxy_schema import ProxySchema
from service.download_abstract_service import DownloadAbstractService

from service.proxy_abstract_service import ProxyAbstractService
from settings import POSIX_MEDIA_DIR
from utils.stream_mapper import dlp_parser, stream_dlp_to_schema, dlp_filter
import copy


class DownloadYtDlpService(DownloadAbstractService):
    def __init__(self, proxy_service: ProxyAbstractService):
        self.proxy_service = proxy_service
        self.ydl_opts = {
            "socket_timeout": 3,
            "retries": 2,
            "noplaylist": True,
            'merge_output_format': "mp4",
        }

    def sleep(self):
        delay = random.randint(2, 5)
        print(f'Sleeping for {delay} seconds')
        time.sleep(delay)

    def get_ydl_options(self, proxy_list: List[ProxySchema], cookie_file: str | None = None):
        ydl_opts = copy.deepcopy(self.ydl_opts)

        ydl_opts["cookiefile"] = cookie_file
        if proxy_list is not None:
            ydl_opts["proxy"] = random.choice(proxy_list).url
        else:
            raise HTTPException(status_code=404, detail="The proxy is not working")
        return ydl_opts


    async def get_video_info(self, video_url: str, filter_query: FilterParams, proxy_url: str | None = None,
                             cookie_file: str | None = None):

        def extract_info():
            self.sleep()
            ydl_opts = self.get_ydl_options([ProxySchema(url=proxy_url)], cookie_file)
            with YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(video_url, download=False)
                info = dlp_parser(info)
                info_schema = [stream_dlp_to_schema(stream) for stream in info]
                info_schema = dlp_filter(info_schema, filter_query)
                return info_schema

        info = await asyncio.to_thread(extract_info)
        return info

    async def download_video(self, video_url: str, proxy_url: str, filter_query: ResolutionFilter, cookie_file: str | None = None):

        file_path = await asyncio.to_thread(self.download_video_sync, video_url, proxy_url, filter_query, cookie_file)
        return FileResponse(path=file_path, filename="video.mp4", media_type="application/octet-stream")

    def download_video_sync(self, video_url: str, proxy_url: str, filter_query: ResolutionFilter,
                            cookie_file: str):

        if filter_query.resolution is None:
            filter_query.resolution = "360p"


        filename_path = POSIX_MEDIA_DIR + "/" + datetime.now().strftime("%Y%m%d-%H%M%S-%f")
        filename_path += ".mp4"

        ydl_opts = self.get_ydl_options([ProxySchema(url=proxy_url)], cookie_file)
        ydl_opts['format'] = f"bestvideo[height={filter_query.resolution[:len(str(filter_query.resolution)) - 1]}]+bestaudio[ext=m4a]/best[ext=mp4]"
        ydl_opts['outtmpl'] = filename_path


        self.sleep()
        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([video_url])

        return filename_path


    async def get_fastest_video(self, video_url: str, proxy_url: str | None = None, cookie_file: str | None = None):
        def extract_info():
            self.sleep()
            ydl_opts = self.get_ydl_options([ProxySchema(url=proxy_url)], cookie_file)
            with YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(video_url, download=False)
                info = dlp_parser(info)
                info_schema = [stream_dlp_to_schema(stream) for stream in info]
                info_schema = dlp_filter(info_schema, FilterParams(progressive=True))
                return info_schema

        info = await asyncio.to_thread(extract_info)
        return info[0]
