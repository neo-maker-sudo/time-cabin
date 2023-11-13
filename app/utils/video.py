import ffmpeg_streaming
from pathlib import PosixPath
from typing import Optional


def mp4_to_m3u8(source: str, filename: str, destination: Optional[PosixPath] = None) -> PosixPath:
    video = ffmpeg_streaming.input(source)
    hls = video.hls(ffmpeg_streaming.Formats.h264())
    hls.auto_generate_representations()
    hls.output(f"{destination}/{filename}.m3u8", async_run=False)
