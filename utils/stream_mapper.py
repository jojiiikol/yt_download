from typing import List, Dict

from pytubefix import Stream

from filter.video_filter import FilterParams
from schema.stream_schema import StreamSchema, StreamDlpSchema


def stream_pytubefix_to_schema(stream: Stream) -> StreamSchema:
    stream_schema = StreamSchema(
        itag=str(stream.itag),
        title=stream.title,
        size=stream.filesize_mb,
        download_url=stream.url,
        video_codec=stream.video_codec,
        audio_codec=stream.audio_codec,
        resolution=stream.resolution,
    )
    return stream_schema

def stream_dlp_to_schema(video_info: Dict) -> StreamSchema:
    stream_schema = StreamSchema(
        itag=video_info["itag"],
        title=video_info["title"],
        size=video_info["size"],
        download_url=video_info["url"],
        video_codec=video_info["vcodec"],
        audio_codec=video_info["acodec"],
        resolution=video_info["resolution"],
    )
    return stream_schema

def dlp_parser(video_info: Dict) -> List[Dict]:
    title = video_info.get('title')
    formats = video_info.get('formats', [])
    result = []
    for format in formats:
        video_info = {}
        url = format.get('url', None)
        if not url:
            continue

        itag = format.get('format_id')
        resolution = format.get('resolution').split("x")[1] + "p" if format.get('resolution') != "audio only" else None
        size = format.get('filesize')
        vcodec = None if format.get('vcodec') == "none" else format.get('vcodec')
        acodec = None if format.get('acodec') == "none" else format.get('acodec')

        if vcodec is None and acodec is None:
            continue
        video_info["itag"] = itag
        video_info["title"] = title
        video_info["size"] = round(size / 1024 / 1024, 3)
        video_info["resolution"] = resolution
        video_info["vcodec"] = vcodec
        video_info["acodec"] = acodec
        video_info["url"] = url
        result.append(video_info)
    return result

def dlp_filter(dlp_data: List[StreamSchema], filters: FilterParams) -> List[StreamSchema]:
    result = []
    for item in dlp_data:

        if filters.progressive:
            if item.video_codec and item.audio_codec:
                return [item]

        if filters.resolution and item.resolution != filters.resolution:
            continue

        if filters.only_audio:
            if item.video_codec or not item.audio_codec:
                continue

        if filters.only_video:
            if not item.video_codec or item.audio_codec:
                continue

        result.append(item)
    return result