from concurrent.futures import ThreadPoolExecutor
from src.video_downloader.backend.models.download_job import DownloadJob, JobStatus
from src.video_downloader.backend.yt_dlp.extractor import YtDlpExtractor
from .yt_dlp.downloader import YtDlpDownloader


class DownloadManager:
    def __init__(self, worker_count=3):
        self.download_executor = ThreadPoolExecutor(max_workers=worker_count)
        # below for future reference
        # self.metadata_executor = ThreadPoolExecutor(max_workers=worker_count) # incase i want to extract metadata for multiple links in future
        
    def submit_download(self, job : DownloadJob):
        self.download_executor.submit(self._download, job)

    def _download(self, job : DownloadJob):
        try:
            job.status = JobStatus.DOWNLOADING

            YtDlpDownloader().download(job)

            job.status = JobStatus.COMPLETED

        except Exception as exc:
            job.status = JobStatus.FAILED
            job.error = str(exc)
    
        
    def shutdown(self):
        self.download_executor.shutdown(wait=True)
            
        