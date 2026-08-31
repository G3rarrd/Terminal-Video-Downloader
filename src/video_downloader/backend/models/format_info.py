from dataclasses import dataclass
from enum import Enum

class FormatType(Enum):
    VIDEO_ONLY = "video_only"
    AUDIO_ONLY = "audio_only"
    COMBINED = "combined"
    UNKNOWN = "unknown" 
 
@dataclass
class FormatInfo:
    format_id: str | None
    extension: str | None

    resolution: str | None
    width: int | None
    height: int | None
    fps: float | None

    filesize: int | None
    filesize_approx: int | None

    video_codec: str | None
    audio_codec: str | None

    video_ext: str | None
    audio_ext: str | None

    bitrate: float | None
    video_bitrate: float | None
    audio_bitrate: float | None

    format_note: str | None
    protocol: str | None
    
    format_type : FormatType=FormatType.UNKNOWN