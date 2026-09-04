from dataclasses import dataclass
from pathlib import Path

from src.video_downloader.models.format_info import FormatInfo

@dataclass
class DownloadRequests:
    url : str
    filename: str
    format: FormatInfo
    output_dir: Path