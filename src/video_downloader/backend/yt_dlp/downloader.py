from src.video_downloader.backend.models.download_job import DownloadJob
from src.video_downloader.backend.models.format_info import FormatInfo, FormatType
import yt_dlp

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
        
        ydl_opts = {
            "format": selector,
            "outtmpl": str(job.output_dir / f"{filename}.%(ext)s"),
            "quiet": True,
            "no_warnings": True,
            "merge_output_format": output_fmt,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([job.url])