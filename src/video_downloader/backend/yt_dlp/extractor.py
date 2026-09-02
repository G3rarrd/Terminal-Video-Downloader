from typing import Optional

import yt_dlp

from src.video_downloader.backend.models.format_info import FormatType
from src.video_downloader.backend.models.media_info import MediaInfo
from src.video_downloader.backend.models.format_info import FormatInfo
from src.video_downloader.backend.yt_dlp.config import get_ytdlp_opts


class YtDlpExtractor:
    def _classify_format(
        self,
        vcodec: Optional[str],
        acodec: Optional[str]
    ) -> FormatType:

        has_video = vcodec not in (None, "none")
        has_audio = acodec not in (None, "none")

        if has_video and has_audio:
            return FormatType.COMBINED

        if has_video:
            return FormatType.VIDEO_ONLY

        if has_audio:
            return FormatType.AUDIO_ONLY

        return FormatType.UNKNOWN
    
    def extract_metadata(self, url : str)-> MediaInfo:
        ydl_opts = get_ytdlp_opts()
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)

            return MediaInfo(
                title=info.get("title"),
                uploader=info.get("uploader"),
                duration=info.get("duration"),
                thumbnail=info.get("thumbnail"),
                webpage_url=info.get("webpage_url"),
                formats=self._parse_formats(info)
            )
            
    def _parse_formats(self, info: dict) -> list[FormatInfo]:
        formats = []

        for fmt in info.get("formats", []):
            acodec = fmt.get("acodec")
            vcodec = fmt.get("vcodec")

            formats.append(FormatInfo(
                    format_id=fmt.get("format_id"),
                    extension=fmt.get("ext"),
                    resolution=fmt.get("resolution"),
                    width=fmt.get("width"),
                    height=fmt.get("height"),
                    fps=fmt.get("fps"),
                    filesize=fmt.get("filesize"),
                    filesize_approx=fmt.get("filesize_approx"),
                    video_codec=vcodec,
                    audio_codec=acodec,
                    audio_ext=fmt.get("audio_ext"),
                    video_ext=fmt.get("video_ext"),
                    bitrate=fmt.get("tbr"),
                    video_bitrate=fmt.get("vbr"),
                    audio_bitrate=fmt.get("abr"),
                    format_note=fmt.get("format_note"),
                    protocol=fmt.get("protocol"),
                    format_type=self._classify_format(vcodec, acodec)
                )
            )
        return formats