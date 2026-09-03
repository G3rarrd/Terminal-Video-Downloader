from src.video_downloader.backend.models.format_info import FormatInfo, FormatType


class FormatProcessor:
    def get_video_formats(self, formats : list[FormatInfo]) -> list[FormatInfo]:
        formats = self._remove_invalid(formats)
        formats = self._select_best_video_formats(formats)
        
        video_formats = [
            f
            for f in formats
            if f.format_type not in (FormatType.AUDIO_ONLY, FormatType.UNKNOWN)
        ]
        
        # Fallback incase video formats are considered UNKNOWN in some sites
        return video_formats if len(video_formats) > 0 else formats
        
    def get_audio_formats(self, formats: list[FormatInfo]) -> list[FormatInfo]:
        formats = self._remove_invalid(formats)
        formats = self._select_best_audio_formats(formats)
        audio_formats =[
            f
            for f in formats
            if f.format_type == FormatType.AUDIO_ONLY
        ]
        return audio_formats
    
    def _remove_invalid(self, formats: list[FormatInfo]) -> list[FormatInfo]:
        return [
            fmt
            for fmt in formats
            if fmt.format_id is not None
        ]
        
    def _select_best_audio_formats(
        self,
        formats: list[FormatInfo]
    ) -> list[FormatInfo]:

        unique : dict[tuple[str, str], FormatInfo]= {}

        for fmt in formats:
            key = (
                fmt.audio_codec,
                fmt.extension,
            )

            current = unique.get(key)

            if current is None:
                unique[key] = fmt
                continue

            current_bitrate = current.audio_bitrate or 0
            new_bitrate = fmt.audio_bitrate or 0

            if new_bitrate > current_bitrate:
                unique[key] = fmt

        return list(unique.values())

    def _select_best_video_formats(self, formats: list[FormatInfo]) -> list[FormatInfo]:
        unique : dict[tuple[str, str], FormatInfo]= {}

        for fmt in formats:
            key = (fmt.height, fmt.extension, fmt.video_codec)

            current = unique.get(key)

            if current is None:
                unique[key] = fmt
                continue

            current_bitrate = current.video_bitrate or 0
            new_bitrate = fmt.video_bitrate or 0

            if new_bitrate > current_bitrate:
                unique[key] = fmt

        return list(unique.values())