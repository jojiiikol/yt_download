from abc import ABC, abstractmethod

from service.download_abstract_service import DownloadAbstractService


class CombineAbstractService(ABC):
    @abstractmethod
    def combine(self, video_path: str, audio_path: str):
        pass
