from typing import Callable, Protocol
from threading import Lock
from uuid import UUID
from ..models.download_progress import DownloadProgress

class ProgressListener(Protocol):
    def __call__(self, progress: DownloadProgress) -> None: ...

class DownloadEventBus:
    
    def __init__(self):
        # self._listeners : list[ProgressListener] = []
        self._job_listeners: dict[UUID, list[ProgressListener]] = {}
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
        
    def _unsubscribe_job(self, job_id: UUID, listener: ProgressListener) -> None:
        with self._lock:
            listeners = self._job_listeners.get(job_id, [])
            if listener in listeners:
                listeners.remove(listener)