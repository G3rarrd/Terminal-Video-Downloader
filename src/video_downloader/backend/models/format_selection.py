from dataclasses import dataclass

from .format_info import FormatInfo

from .media_info import MediaInfo


@dataclass
class FormatSelection:
    media : MediaInfo
    video_formats : list[FormatInfo]
    audio_formats : list[FormatInfo]