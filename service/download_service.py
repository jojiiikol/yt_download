import urllib.error
from datetime import datetime
from typing import List, Dict

from fastapi import HTTPException
import os
from yt_dlp import YoutubeDL, DownloadError

from exceptions.connect_exeption import connect_exception
from exceptions.streams_exception import is_empty_streams
from filter.video_filter import BaseFilter, FilterParams, ResolutionFilter
import asyncio

from schema.stream_schema import StreamPytubefixSchema
from service.combine_service import CombineFfmpegService
from service.download_abstract_service import DownloadAbstractService
from pytubefix import YouTube as ptf_yt, Stream
from pytubefix import exceptions as ptf_yt_exceptions

from utils.filename_maker import get_filename
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
        audio = None
        stream = video.streams.filter(**filter_query.model_dump(), type="video").desc().first()
        is_empty_streams(stream)
        if not stream.audio_codec:
            audio = video.streams.filter(mime_type="audio/mp4").order_by('filesize').desc().first()
        # filespath = await self.download_streams(stream, audio)
        cfs = CombineFfmpegService()
        await cfs.combine(**{
            "video_path": os.path.abspath("20250924-151725.webm"),
            "audio_path": os.path.abspath("20250924-151807.m4a")
        })
        return stream_pytubefix_to_schema(stream)

    async def download_streams(self, video_stream: Stream, audio_stream: Stream | None = None) -> Dict[str: str, str: str | None]:
        video = video_stream.download(filename=get_filename(video_stream.default_filename), skip_existing=False)
        audio = None
        if audio_stream is not None:
            audio = audio_stream.download(filename=get_filename(audio_stream.default_filename), skip_existing=False)
        return {
            "video_path": video,
            "audio_path": audio,
        }


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
                try:
                    info = ydl.extract_info(video_url, download=False)
                except DownloadError as e:
                    raise HTTPException(status_code=500, detail="Unknown error from yt-dlp. Please try use pytubefix library")
                info = dlp_parser(info)
                info_schema = [stream_dlp_to_schema(stream) for stream in info]
                info_schema = dlp_filter(info_schema, filter_query)
                return info_schema
        info = await asyncio.to_thread(extract_info)
        return info

    async def download_video(self, stream_id: int):
        pass

    async def get_fastest_video(self, video_url: str):
        def extract_info():
            with YoutubeDL() as ydl:
                info = ydl.extract_info(video_url, download=False)
                info = dlp_parser(info)
                info_schema = [stream_dlp_to_schema(stream) for stream in info]
                info_schema = dlp_filter(info_schema, FilterParams(progressive=True))
                return info_schema
        info = await asyncio.to_thread(extract_info)
        return info