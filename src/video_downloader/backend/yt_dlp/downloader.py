from datetime import datetime


from yt_dlp.utils import DownloadCancelled
from src.video_downloader.models.download_job import CancellationToken, DownloadJob
from src.video_downloader.models.download_progress import DownloadProgress, JobStatus
from src.video_downloader.models.format_info import FormatInfo, FormatType
import yt_dlp
from typing import Callable, Optional
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

    def download(
        self, job: DownloadJob, 
        publish: Callable[[DownloadProgress], None], 
        token: CancellationToken
    ):

        publish(DownloadProgress(
            job_id=job.id,
            status=JobStatus.QUEUED,
            started_at=datetime.now(),
        ))
        
        output_fmt = self._build_merge_format(job.format)
        
        selector = self._build_selector(job.format)
        
        filename = job.filename or "%(title)s"
        try:
            ydl_extra_opts = {
                "format": selector,
                "outtmpl": str(job.output_dir / f"{filename}.%(ext)s"),
                "merge_output_format": output_fmt,
                "socket_timeout": 10,
                "progress_hooks" : [lambda data : self._on_ytdlp_progress(job, data, publish, token)]
            }
            
            ydl_opts = get_ytdlp_opts(ydl_extra_opts)
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([job.url])
                
            publish(DownloadProgress(
                job_id=job.id,
                status=JobStatus.COMPLETED,
                progress_pct=100.0,
                completed_at=datetime.now()
            ))
            
        except DownloadCancelled as cd:
            publish(DownloadProgress(
                job_id=job.id, 
                status=JobStatus.CANCELLED
            ))
            raise
            
        except Exception as e:
            publish(DownloadProgress(
                job_id=job.id,
                status=JobStatus.ERROR,
                error=str(e),
            ))
            raise
    
    def _on_ytdlp_progress(
        self, 
        job: DownloadJob, 
        data:dict, 
        publish: Callable[[DownloadProgress], None],
        token : CancellationToken,
    ):

        if token.is_cancelled():
            raise DownloadCancelled("User cancelled download")
        
        progress = self._build_progress(job, data)
        if progress:
            publish(progress)
    
    def _build_progress(self, job : DownloadJob, data : dict) -> Optional[DownloadProgress]:
        status = data.get("status")
        
        match status:
            case "downloading":

                downloaded_bytes = data.get("downloaded_bytes", 0)
                
                total_bytes = (
                    data.get("total_bytes")
                    or data.get("total_bytes_estimate")
                    or 0
                )
                
                percentage = (downloaded_bytes / total_bytes * 100) if total_bytes else 0.0
                
                return DownloadProgress(
                    job_id=job.id,
                    status=JobStatus.DOWNLOADING,
                    progress_pct=percentage,
                    downloaded_bytes=downloaded_bytes,
                    total_bytes=total_bytes,
                    speed=data.get("speed", 0.0),
                    eta=data.get("eta", 0)
                )
                
            case "finished":
                return DownloadProgress(job_id=job.id, status=JobStatus.PROCESSING, progress_pct=100.0)
            
            case "error":
                return DownloadProgress(job_id=job.id, status=JobStatus.ERROR, error=data.get("error"))
            
            case _:
                return None
            
            

        
    