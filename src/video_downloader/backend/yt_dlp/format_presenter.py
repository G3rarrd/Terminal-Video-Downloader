from src.video_downloader.backend.models.format_info import FormatInfo, FormatType


class FormatPresenter:
    def _format_resolution(self, fmt: FormatInfo) -> str:
        resolution = fmt.resolution

        if resolution:
            if resolution.endswith("p"):
                return resolution

            if "x" in resolution:
                width, height = resolution.split("x")
                return f"{min(int(width), int(height))}p"

            return resolution
        
        # Height and/or width might not be empty
        dimensions = [
            dimension
            for dimension in (fmt.width, fmt.height)
            if dimension is not None
        ]

        if dimensions:
            return f"{min(dimensions)}p"

        return "-"

    
    def video_row(self, fmt: FormatInfo) -> list[str]:
        if fmt.format_type == FormatType.AUDIO_ONLY:
            raise ValueError(f"Expected video/combined format, got {fmt.format_type}")
        
        return [
            self._format_resolution(fmt) or "-",
            fmt.fps or "-",
            fmt.video_codec or "-",
            fmt.video_bitrate or "-",
            fmt.filesize or "-",
            fmt.extension or "-",
        ]

    def audio_row(self, fmt: FormatInfo) -> list[str]:
        if fmt.format_type != FormatType.AUDIO_ONLY:
            raise ValueError(f"Expected audio format, got {fmt.format_type}")
        
        return [
            fmt.audio_codec,
            fmt.audio_bitrate,
            fmt.filesize,
            fmt.extension or "-",
        ]