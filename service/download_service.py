import urllib.error

from fastapi import HTTPException
from yt_dlp import YoutubeDL

from exceptions.connect_exeption import connect_exception
from exceptions.streams_exception import is_empty_streams
from filter.video_filter import BaseFilter, FilterParams, ResolutionFilter
import asyncio

from schema.stream_schema import StreamPytubefixSchema
from service.download_abstract_service import DownloadAbstractService
from pytubefix import YouTube as ptf_yt
from pytubefix import exceptions as ptf_yt_exceptions

from utils.stream_mapper import stream_pytubefix_to_schema, dlp_parser, stream_dlp_to_schema, dlp_filter
import json


class DownloadPytubefixService(DownloadAbstractService):
    async def get_video_info(self, video_url: str, filter_query: FilterParams):
        video = ptf_yt(video_url)
        try:
            video.check_availability()
            streams = video.streams.filter(**filter_query.model_dump())
            streams = [stream_pytubefix_to_schema(stream) for stream in streams]
            return streams
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    async def download_video(self, video_url: str, filter_query: ResolutionFilter):
        video = ptf_yt(video_url)
        streams = video.streams.filter(**filter_query.model_dump(), type="video").desc().first()
        is_empty_streams(streams)
        return stream_pytubefix_to_schema(streams)

    async def get_fastest_video(self, video_url: str):
        video = ptf_yt(video_url)
        try:
            video.check_availability()
            stream = video.streams.get_highest_resolution()
            stream = stream_pytubefix_to_schema(stream)
            return stream
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

class DownloadYtDlpService(DownloadAbstractService):
    async def get_video_info(self, video_url: str, filter_query: FilterParams):
        def extract_info():
            with YoutubeDL() as ydl:
                info = ydl.extract_info(video_url, download=False)
                info = dlp_parser(info)
                info_schema = [stream_dlp_to_schema(stream) for stream in info]
                info_schema = dlp_filter(info_schema, filter_query)
                return info_schema
        info = await asyncio.to_thread(extract_info)
        return info

    async def download_video(self, stream_id: int):
        pass

    async def get_fastest_video(self, stream_id: int):
        pass