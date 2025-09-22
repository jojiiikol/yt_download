from pytubefix import Stream

from schema.stream_schema import StreamSchema


def stream_to_schema(stream: Stream) -> StreamSchema:
    stream_schema = StreamSchema(
        itag=stream.itag,
        title=stream.title,
        size=stream.filesize_mb,
        download_url=stream.url,
        video_codec=stream.video_codec,
        audio_codec=stream.audio_codec,
        resolution=stream.resolution,
    )
    return stream_schema