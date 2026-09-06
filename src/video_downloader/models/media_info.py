from src.video_downloader.models.format_info import FormatInfo
from dataclasses import dataclass
from PIL import Image as PILImage

@dataclass
class MediaInfo:
    title: str | None
    uploader: str | None
    duration: int | None
    thumbnail_img: PILImage.Image | None
    domain: str | None
    webpage_url: str
    formats : list[FormatInfo] | None