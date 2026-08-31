from src.video_downloader.backend.models.format_info import FormatInfo
from dataclasses import dataclass

@dataclass
class MediaInfo:
    title: str | None
    uploader: str | None
    duration: int | None
    thumbnail: str | None
    webpage_url: str
    formats : list[FormatInfo] | None