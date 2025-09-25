from pydantic import BaseModel


class StreamSchema(BaseModel):
    itag: str
    title: str | None = None
    size: float | None = None
    download_url: str | None = None
    video_codec: str | bool | None = None
    audio_codec: str | bool | None = None
    resolution: str | None = None


class StreamDlpSchema(BaseModel):
    itag: str
    title: str | None = None
    size: float | None = None
    download_url: str | None = None
    video_codec: str | bool | None = None
    audio_codec: str | bool | None = None
    resolution: str | None = None