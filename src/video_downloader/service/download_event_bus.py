from typing import Callable, Protocol
from threading import Lock
from uuid import UUID
from ..models.download_progress import AggregateProgress, DownloadProgress, JobStatus

_TERMINAL_STATUSES = {JobStatus.COMPLETED, JobStatus.ERROR, JobStatus.CANCELLED}
class ProgressListener(Protocol):
    def __call__(self, progress: DownloadProgress) -> None: ...

class TotalProgressListener(Protocol):
    def __call__(self, progress: AggregateProgress) -> None: ...
class DownloadEventBus:
    
    def __init__(self):
        # self._listeners : list[ProgressListener] = []
        self._job_listeners: dict[UUID, list[ProgressListener]] = {}
        self._total_listeners: list[TotalProgressListener] = []
        self._latest_speeds: dict[UUID, float] = {}
        self._downloaded_bytes: dict[UUID, int] = {}  # NEW — per-job cumulative total
        self._lock = Lock()
        
        
    # def subscribe(self, listener : ProgressListener) -> Callable[[], None]:
    #     with self._lock:
    #         self._listeners.append(listener)
            
    #     return lambda: self._unsubscribe(listener)
    
    # def _unsubscribe(self, listener: ProgressListener) -> None:
    #     with self._lock:
    #         if listener in self._listeners:
    #             self._listeners.remove(listener)
    
    def subscribe_to_job(self, job_id: UUID, listener: ProgressListener) -> Callable[[], None]:
        with self._lock:
            self._job_listeners.setdefault(job_id, []).append(listener)
            
        return lambda : self._unsubscribe_job(job_id, listener)
        
    def _unsubscribe_job(
        self, 
        job_id: UUID, 
        listener: ProgressListener
    ) -> None:
        with self._lock:
            listeners = self._job_listeners.get(job_id, [])

            if listener in listeners:
                listeners.remove(listener)
                
    def subscribe_to_total_progress(self, listener: TotalProgressListener) -> Callable[[], None]:
        with self._lock:
            self._total_listeners.append(listener)

        return lambda: self._unsubscribe_total(listener)

    def _unsubscribe_total(self, listener: TotalProgressListener) -> None:
        with self._lock:
            if listener in self._total_listeners:
                self._total_listeners.remove(listener)
                
    def publish(self, progress: DownloadProgress) -> None:
        with self._lock:
            job_listeners = list(self._job_listeners.get(progress.job_id, []))
            
            if progress.status in _TERMINAL_STATUSES:
                self._latest_speeds.pop(progress.job_id, None)
            else:
                self._latest_speeds[progress.job_id] = max(0.0, progress.speed or 0.0)

            # will still be needed even after the download is finsihed
            self._downloaded_bytes[progress.job_id] = progress.downloaded_bytes
            aggregate = AggregateProgress(
                total_speed=sum(self._latest_speeds.values()),
                active_job_count=len(self._latest_speeds),
                total_downloaded_bytes=sum(self._downloaded_bytes.values()),
            )
            total_listeners = list(self._total_listeners)
            
        for listener in job_listeners:
            try:
                listener(progress)
            except Exception:
                pass
            
        for listener in total_listeners:
            try:
                listener(aggregate)
            except Exception:
                pass
                
    