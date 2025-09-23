from typing import Literal

from pydantic import BaseModel

class BaseFilter(BaseModel):
    pass

class ResolutionFilter(BaseFilter):
    resolution: Literal["144p", "240p", "360p", "480p", "720p", "1080p", "1280p", "1440p"] | None = None

class FilterParams(ResolutionFilter):
    progressive: bool | None = None
    only_audio: bool = False
    only_video: bool = False



