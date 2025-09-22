import urllib.error

from fastapi import HTTPException
from yt_dlp import YoutubeDL

from exceptions.connect_exeption import connect_exception
from schema.stream_schema import StreamSchema
from service.download_abstract_service import DownloadAbstractService
from pytubefix import YouTube as ptf_yt
from pytubefix import exceptions as ptf_yt_exceptions

from utils.stream_mapper import stream_to_schema
import json


class DownloadPytubefixService(DownloadAbstractService):
    async def get_video_info(self, video_url: str):
        video = ptf_yt(video_url)
        try:
            video.check_availability()
            streams = video.streams
            streams = [stream_to_schema(stream) for stream in streams]
            return streams
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    async def download_video(self, stream_id: int):
        pass

class DownloadYtDlpService(DownloadAbstractService):
    async def get_video_info(self, video_url: str):
        with YoutubeDL() as ydl:
            list_url = [video_url]
            info = ydl.extract_info(video_url, download=False)
            return ydl.sanitize_info(info)

    async def download_video(self, stream_id: int):
        pass