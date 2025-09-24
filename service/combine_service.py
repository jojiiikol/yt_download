from pathlib import Path

from service.combine_abstract_service import CombineAbstractService
from ffmpeg import FFmpeg
import os

from settings import POSIX_MEDIA_DIR
from utils.filename_maker import get_filename, get_posix_path


class CombineFfmpegService(CombineAbstractService):
    async def combine(self, video_path: str, audio_path: str) -> str:
        output_path = get_posix_path(os.path.join(POSIX_MEDIA_DIR, get_filename("a.mp4")))
        ffmpeg = (
            FFmpeg().input(video_path).input(audio_path).output(output_path, vcodec="copy", acodec="copy")
        )
        ffmpeg.execute()
        return output_path