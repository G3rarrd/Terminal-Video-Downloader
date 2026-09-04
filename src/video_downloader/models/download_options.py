from dataclasses import dataclass
from pathlib import Path

@dataclass
class DownloadOptions:
    video_quality: str
    audio_quality: str
    output_format: str
    output_directory: Path