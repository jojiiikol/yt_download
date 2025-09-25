from abc import ABC, abstractmethod


class CombineAbstractService(ABC):
    @abstractmethod
    def combine(self, video_path: str, audio_path: str) -> str:
        pass
