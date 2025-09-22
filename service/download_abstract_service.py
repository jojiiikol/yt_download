from abc import ABC, abstractmethod


class DownloadAbstractService(ABC):

    @abstractmethod
    async def get_video_info(self, video_url: str):
        pass

    @abstractmethod
    async def download_video(self, stream_id: int):
        pass
