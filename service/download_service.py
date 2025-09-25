from datetime import datetime
from typing import Dict


from starlette.responses import FileResponse
from yt_dlp import YoutubeDL

from exceptions.streams_exception import is_empty_streams
from filter.video_filter import FilterParams, ResolutionFilter
import asyncio

from service.combine_abstract_service import CombineAbstractService
from service.download_abstract_service import DownloadAbstractService
from pytubefix import YouTube as ptf_yt, Stream

from settings import POSIX_MEDIA_DIR
from utils.filename_maker import get_filename, get_posix_path
from utils.stream_mapper import stream_pytubefix_to_schema, dlp_parser, stream_dlp_to_schema, dlp_filter

class DownloadPytubefixService(DownloadAbstractService):
    def __init__(self, combine_service: CombineAbstractService):
        self.combine_service = combine_service

    async def get_video_info(self, video_url: str, filter_query: FilterParams):
        video = await asyncio.to_thread(ptf_yt, video_url)
        video.check_availability()
        streams = video.streams.filter(**filter_query.model_dump())
        streams = [stream_pytubefix_to_schema(stream) for stream in streams]
        return streams

    async def download_video(self, video_url: str, filter_query: ResolutionFilter):
        video = await asyncio.to_thread(ptf_yt, video_url)
        audio = None

        stream = video.streams.filter(**filter_query.model_dump(), type="video").desc().first()
        is_empty_streams(stream)
        if not stream.audio_codec:
            audio = video.streams.filter(mime_type="audio/mp4").order_by('filesize').desc().first()

        files_path = await asyncio.to_thread(self.download_streams, stream, audio)
        result_path = await asyncio.to_thread(self.combine_service.combine, files_path.get("video_path"), files_path.get("audio_path"))

        return FileResponse(path=result_path, filename="video.mp4", media_type="application/octet-stream")

    def download_streams(self, video_stream: Stream, audio_stream: Stream | None = None) -> Dict[str: str, str: str | None]:
        video = video_stream.download(filename=get_filename(video_stream.default_filename), output_path=POSIX_MEDIA_DIR, skip_existing=False)
        audio = None

        if audio_stream is not None:
            audio = audio_stream.download(filename=get_filename(audio_stream.default_filename), output_path=POSIX_MEDIA_DIR, skip_existing=False)

        return {
            "video_path": get_posix_path(video),
            "audio_path": get_posix_path(audio),
        }

    async def get_fastest_video(self, video_url: str):
        video = ptf_yt(video_url)
        video.check_availability()
        stream = video.streams.get_highest_resolution()
        stream = stream_pytubefix_to_schema(stream)
        return stream

class DownloadYtDlpService(DownloadAbstractService):
    def __init__(self, combine_service: CombineAbstractService):
        self.combine_service = combine_service

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

    async def download_video(self, video_url: str, filter_query: ResolutionFilter):
        file_path = await asyncio.to_thread(self.download_video_sync, video_url, filter_query)
        return FileResponse(path=file_path, filename="video.mp4", media_type="application/octet-stream")

    def download_video_sync(self, video_url: str, filter_query: ResolutionFilter):
        filename_path = POSIX_MEDIA_DIR + "/" + datetime.now().strftime("%Y%m%d-%H%M%S%f")
        ydl_opts = {
            "format": f"bestvideo[height={filter_query.resolution[:len(str(filter_query.resolution)) - 1]}]+bestaudio",
            'merge_output_format': None,
            "outtmpl": filename_path,
            "postprocessors": [{
                "key": "FFmpegVideoConvertor",
                "preferedformat": "mp4"
            }],
        }
        filename_path += ".mp4"
        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([video_url])

        return filename_path

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
