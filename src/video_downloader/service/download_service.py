from src.video_downloader.models.download_requests import DownloadRequests

from ..backend.yt_dlp.format_processor import FormatProcessor
from ..backend.yt_dlp.extractor import YtDlpExtractor

from .download_manager import DownloadManager

from ..models.format_selection import FormatSelection
from ..models.download_job import DownloadJob
from ..models.format_info import FormatInfo

class DownloadService:
    def __init__(self, manager : DownloadManager):
        self.manager = manager
        
    def add_download_job(self, request : DownloadRequests):
        job = DownloadJob(
            url=request.url,
            format=request.format,
            filename=request.filename,
            output_dir=request.output_dir
        )
        
        self.manager.submit_download(job)
        
        return job
        
    def extract_metadata(self, url : str):
        processor = FormatProcessor()
        media = YtDlpExtractor().extract_metadata(url)
        video : list[FormatInfo] = processor.get_video_formats(media.formats)
        audio : list[FormatInfo] = processor.get_audio_formats(media.formats)
        return FormatSelection(
            media=media,
            video_formats=video,
            audio_formats=audio
        )