from concurrent.futures import Future, ThreadPoolExecutor
from threading import Lock
from typing import Callable
from uuid import UUID
import traceback
from yt_dlp.utils import DownloadCancelled

from src.video_downloader.service.download_event_bus import DownloadEventBus, ProgressListener

from ..models.download_progress import DownloadProgress, JobStatus
from ..models.download_job import CancellationToken, DownloadJob
from ..backend.yt_dlp.downloader import YtDlpDownloader

class DownloadManager:
    def __init__(self, events : DownloadEventBus,  worker_count=3):
        self._download_executor = ThreadPoolExecutor(max_workers=worker_count)
        self._events : DownloadEventBus = events
        self._downloader = YtDlpDownloader()
        self._tokens : dict[UUID, CancellationToken]= {}
        self._futures : dict[UUID, Future] = {}
        self._lock = Lock()

    def cancel(self, job_id : UUID):
        future = None
        cancel_token = None
        with self._lock:
            future = self._futures.get(job_id, None)
            cancel_token = self._tokens.get(job_id, None)
            
        if future is None:
            return False
        
        if future.cancel():
            self._events.publish(DownloadProgress(job_id=job_id, status=JobStatus.CANCELLED))
            return True
        
        if cancel_token is not None:
            cancel_token.cancel()
            return True   # cancellation requested; actual CANCELLED event arrives async

        return False

    def submit_download(self, job : DownloadJob):
        token = CancellationToken()
        with self._lock:
            self._tokens[job.id] = token
            
        future = self._download_executor.submit(self._download, job, token)
        
        with self._lock:
            self._futures[job.id] = future
        
    def subscribe_to_job(self, job_id: UUID, listener: ProgressListener) -> Callable[[], None]:
        return self._events.subscribe_to_job(job_id, listener)

    def _download(self, job : DownloadJob, token: CancellationToken):
        try:
            self._downloader.download(job, self._events.publish, token)
        except DownloadCancelled :
            self._events.publish(DownloadProgress(
                job_id=job.id, 
                status=JobStatus.CANCELLED
            ))
            raise
        except Exception as exc:
            pass
            
        finally:
            # download completed, cancelled or failed
            with self._lock:
                self._futures.pop(job.id, None)
                self._tokens.pop(job.id, None)
                
    

    def shutdown(self):
        self._download_executor.shutdown(wait=True)
            
        