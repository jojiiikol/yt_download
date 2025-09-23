from fastapi import HTTPException
from pytubefix import StreamQuery, Stream


def is_empty_streams(stream: Stream):
    if not stream:
        raise HTTPException(status_code=404, detail="No streams found, please change resolution filter")