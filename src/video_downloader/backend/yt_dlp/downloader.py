from src.video_downloader.models.download_job import DownloadJob
from src.video_downloader.models.download_progress import JobStatus
from src.video_downloader.models.format_info import FormatInfo, FormatType
import yt_dlp

from src.video_downloader.backend.yt_dlp.config import get_ytdlp_opts

class YtDlpDownloader:
    
    def _build_selector(self, fmt : FormatInfo) -> str:
        if fmt.format_type == FormatType.VIDEO_ONLY:
            return f"{fmt.format_id}+bestaudio/{fmt.format_id}"
            
        return fmt.format_id
    
    def _build_merge_format(self, fmt: FormatInfo) -> str:
        if fmt.extension in ("mp4", "webm", "mkv"):
            return fmt.extension

        return "mp4"

    def download(self, job: DownloadJob):
        output_fmt = self._build_merge_format(job.format)
        
        selector = self._build_selector(job.format)
        
        filename = job.filename or "%(title)s"
        ydl_extra_opts = {
            "format": selector,
            "outtmpl": str(job.output_dir / f"{filename}.%(ext)s"),
            "merge_output_format": output_fmt,
            "progress_hooks" : [lambda data : self._progress_hook(job, data)]
        }
        
        ydl_opts = get_ytdlp_opts(ydl_extra_opts)
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([job.url])
            
    def _progress_hook(self, job : DownloadJob, data : dict):
        if data["status"] == "downloading":
            job.status = JobStatus.DOWNLOADING
            
            job.download_bytes = data.get("download_bytes", 0)
            
            job.total_bytes = (
                data.get("total_bytes")
                or data.get("total_bytes_estimate")
                or 0
            )
            
            job.speed = data.get("speed")
            job.eta = data.get("eta")
            
            if job.total_bytes:
                job.progress = (
                    job.download_bytes / job.total_bytes * 100
                )
                
        elif data["status"] == "finished":
            job.status = JobStatus.PROCESSING
            
            
            

        
    