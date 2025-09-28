import socket
from datetime import datetime
import random
from typing import Dict, List

import socks
from fastapi import HTTPException
from fastapi.params import Form
from starlette.responses import FileResponse
from watchfiles import awatch
from yt_dlp import YoutubeDL, DownloadError

from exceptions.streams_exception import is_empty_streams
from filter.video_filter import FilterParams, ResolutionFilter
import asyncio

from schema.proxy_schema import ProxySchema
from service.combine_abstract_service import CombineAbstractService
from service.download_abstract_service import DownloadAbstractService
from pytubefix import YouTube as ptf_yt, Stream

from service.proxy_abstract_service import ProxyAbstractService
from settings import POSIX_MEDIA_DIR, COOKIES_DIR
from utils.filename_maker import get_filename, get_posix_path
from utils.stream_mapper import stream_pytubefix_to_schema, dlp_parser, stream_dlp_to_schema, dlp_filter
import copy


class DownloadPytubefixService(DownloadAbstractService):
    def __init__(self, combine_service: CombineAbstractService):
        self.combine_service = combine_service

    async def get_video_info(self, video_url: str, filter_query: FilterParams, proxy_url: str | None = None, cookie_file: str | None = None):
        video = await asyncio.to_thread(ptf_yt, video_url)
        await asyncio.to_thread(video.check_availability)
        streams = video.streams.filter(**filter_query.model_dump())
        streams = [stream_pytubefix_to_schema(stream) for stream in streams]
        return streams

    async def download_video(self, video_url: str, filter_query: ResolutionFilter, proxy_url: str | None = None, cookie_file: str | None = None):
        video = await asyncio.to_thread(ptf_yt, video_url)
        await asyncio.to_thread(video.check_availability)
        audio = None

        stream = video.streams.filter(**filter_query.model_dump(), type="video").desc().first()
        is_empty_streams(stream)
        if not stream.audio_codec:
            audio = video.streams.filter(mime_type="audio/mp4").order_by('filesize').desc().first()

        files_path = await asyncio.to_thread(self.download_streams, stream, audio)
        result_path = await asyncio.to_thread(self.combine_service.combine, files_path.get("video_path"),
                                              files_path.get("audio_path"))

        return FileResponse(path=result_path, filename="video.mp4", media_type="application/octet-stream")

    def download_streams(self, video_stream: Stream, audio_stream: Stream | None = None) -> Dict[
        str: str, str: str | None]:

        video = video_stream.download(filename=get_filename(video_stream.default_filename), output_path=POSIX_MEDIA_DIR,
                                      skip_existing=False)
        audio = None

        if audio_stream is not None:
            audio = audio_stream.download(filename=get_filename(audio_stream.default_filename),
                                          output_path=POSIX_MEDIA_DIR, skip_existing=False)

        return {
            "video_path": get_posix_path(video),
            "audio_path": get_posix_path(audio),
        }

    async def get_fastest_video(self, video_url: str, proxy_url: str | None = None, cookie_file: str | None = None):
        video = await asyncio.to_thread(ptf_yt, video_url)
        await asyncio.to_thread(video.check_availability)
        stream = video.streams.get_highest_resolution()
        stream = stream_pytubefix_to_schema(stream)
        return stream


class DownloadYtDlpService(DownloadAbstractService):
    def __init__(self, combine_service: CombineAbstractService, proxy_service: ProxyAbstractService):
        self.combine_service = combine_service
        self.proxy_service = proxy_service
        self.ydl_opts = {
            "socket_timeout": 3,
            "retries": 2,
            "noplaylist": True,
            'merge_output_format': None,
            "postprocessors": [{
                "key": "FFmpegVideoConvertor",
                "preferedformat": "mp4"
            }],
        }

    def get_ydl_options(self, proxy_list: List[ProxySchema], cookie_file: str | None = None):
        ydl_opts = copy.deepcopy(self.ydl_opts)

        if cookie_file is not None:
            ydl_opts["cookiefile"] = cookie_file

        if proxy_list is not None:
            ydl_opts["proxy"] = random.choice(proxy_list).url
        else:
            raise HTTPException(status_code=404, detail="The proxy is not working")
        return ydl_opts


    async def get_video_info(self, video_url: str, filter_query: FilterParams, proxy_url: str | None = None,
                             cookie_file: str | None = None):

        proxy_list = await self.proxy_service.get_all()
        proxy_url = [ProxySchema(url=proxy_url)] if proxy_url else proxy_list

        def extract_info():
            while proxy_url:
                try:
                    ydl_opts = self.get_ydl_options(proxy_url, cookie_file)
                    with YoutubeDL(ydl_opts) as ydl:
                        info = ydl.extract_info(video_url, download=False)
                        info = dlp_parser(info)
                        info_schema = [stream_dlp_to_schema(stream) for stream in info]
                        info_schema = dlp_filter(info_schema, filter_query)
                        return info_schema
                except DownloadError as e:
                    proxy_url.remove(ProxySchema(url=ydl_opts["proxy"]))
            raise HTTPException(status_code=500, detail="The proxy is not working")

        info = await asyncio.to_thread(extract_info)
        return info

    async def download_video(self, video_url: str, filter_query: ResolutionFilter, proxy_url: str | None = None,
                             cookie_file: str | None = None):
        proxy_list = await self.proxy_service.get_all()
        proxy_url = [ProxySchema(url=proxy_url)] if proxy_url else proxy_list
        file_path = await asyncio.to_thread(self.download_video_sync, video_url, proxy_url, filter_query, cookie_file)
        return FileResponse(path=file_path, filename="video.mp4", media_type="application/octet-stream")

    def download_video_sync(self, video_url: str, proxy_list: List[ProxySchema], filter_query: ResolutionFilter,
                            cookie_file: str | None = None):
        if filter_query.resolution is None:
            filter_query.resolution = "360p"

        while proxy_list:
            ydl_opts = self.get_ydl_options(proxy_list, cookie_file)
            filename_path = POSIX_MEDIA_DIR + "/" + datetime.now().strftime("%Y%m%d-%H%M%S")
            ydl_opts['format'] = f"bestvideo[height={filter_query.resolution[:len(str(filter_query.resolution)) - 1]}]+bestaudio"
            ydl_opts['outtmpl'] = filename_path

            filename_path += ".mp4"
            try:
                with YoutubeDL(ydl_opts) as ydl:
                    ydl.download([video_url])

                return filename_path
            except DownloadError as e:
                proxy_list.remove(ProxySchema(url=ydl_opts["proxy"]))
        raise HTTPException(status_code=500, detail="The proxy is not working")

    async def get_fastest_video(self, video_url: str, proxy_url: str | None = None, cookie_file: str | None = None):

        proxy_list = await self.proxy_service.get_all()
        proxy_url = [ProxySchema(url=proxy_url)] if proxy_url else proxy_list

        def extract_info():
            while proxy_url:
                try:
                    ydl_opts = self.get_ydl_options(proxy_url, cookie_file)
                    with YoutubeDL(ydl_opts) as ydl:
                        info = ydl.extract_info(video_url, download=False)
                        info = dlp_parser(info)
                        info_schema = [stream_dlp_to_schema(stream) for stream in info]
                        info_schema = dlp_filter(info_schema, FilterParams(progressive=True))
                        return info_schema
                except DownloadError as e:
                    proxy_url.remove(ProxySchema(url=ydl_opts["proxy"]))
            raise HTTPException(status_code=500, detail="The proxy is not working")

        info = await asyncio.to_thread(extract_info)
        return info[0]
