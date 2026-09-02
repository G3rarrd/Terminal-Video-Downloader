from src.video_downloader.backend.models.format_selection import FormatSelection
from src.video_downloader.backend.models.format_info import FormatInfo
from .format_processor import FormatProcessor
from .extractor import YtDlpExtractor


class FormatOrchestrator:
    def __init__(self):
        self.extractor = YtDlpExtractor()
        self.processor = FormatProcessor()
        
    def inspect_url(self, url : str)-> FormatSelection:
        media = self.extractor.extract_metadata(url)
        video : list[FormatInfo] = self.processor.get_video_formats(media.formats)
        audio : list[FormatInfo] = self.processor.get_audio_formats(media.formats)
        
        return FormatSelection(
            media=media,
            video_formats=video,
            audio_formats=audio
        )