from abc import ABC, abstractmethod
from filter.video_filter import BaseFilter


class DownloadAbstractService(ABC):

    @abstractmethod
    async def get_video_info(self, video_url: str, filter_query: BaseFilter):
        pass

    @abstractmethod
    async def get_fastest_video(self, video_url: str):
        pass

    @abstractmethod
    async def download_video(self, video_url: str, filter_query: BaseFilter):
        pass
