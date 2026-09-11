from pathlib import Path
from typing import Callable
from uuid import UUID

from .download_event_bus import DownloadEventBus, ProgressListener, TotalProgressListener
from ..backend.yt_dlp.format_processor import FormatProcessor
from ..backend.yt_dlp.extractor import YtDlpExtractor

from .download_manager import DownloadManager
from ..models.format_selection import FormatSelection
from ..models.download_job import DownloadJob
from ..models.format_info import FormatInfo

class DownloadService:
    def __init__(self, manager : DownloadManager):
        self._manager = manager
        
    def add_download_job(self, job : DownloadJob):
        self._manager.submit_download(job)
        return job
    
    def cancel_job(self, job_id: UUID) -> bool:
        return self._manager.cancel(job_id)
    
    def open_job(self, job: DownloadJob) -> None:
        file_path = job.output_dir / f"{job.filename}.{job.ext}"
        
        if not file_path.exists():
            raise FileNotFoundError(file_path)
        
        return path
    
    def _start_file(self, filepath : Path):
        system = platform.system()

        if system == "Windows":
            os.startfile(filepath)

        elif system == "Darwin":
            subprocess.run(["open", str(filepath)], check=False)

        elif system == "Linux":
            subprocess.run(["xdg-open", str(filepath)], check=False)
        path = self._construct_format_path(cur_job)
    
    def subscribe_to_job(self, job_id: UUID, listener: ProgressListener) -> Callable[[], None]:
        return self._manager.subscribe_to_job(job_id, listener)
    
    def subscribe_to_total_progress(self, listener: TotalProgressListener) -> Callable[[], None]:
        return self._manager.subscribe_to_total_progress(listener)
    
    def shutdown(self) -> None:
        self._manager.shutdown()
        
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