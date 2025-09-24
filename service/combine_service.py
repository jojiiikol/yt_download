import subprocess

from service.combine_abstract_service import CombineAbstractService
from ffmpeg import FFmpeg

from utils.filename_maker import get_filename


class CombineFfmpegService(CombineAbstractService):
    async def combine(self, video_path: str, audio_path: str):
        print(video_path)
        filename = get_filename("a.mp4")
        ffmpeg = (
            FFmpeg().input("20250924-151725.webm").input("20250924-151807.m4a").output(filename, vcodec="copy", acodec="copy")
        )


        ffmpeg.execute()