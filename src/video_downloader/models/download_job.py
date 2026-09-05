from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID
from .format_info import FormatInfo
from .media_info import MediaInfo
from enum import Enum
from pathlib import Path
from uuid import UUID, uuid4

from threading import Event
@dataclass(frozen=True)
class DownloadJob:
    url: str
    format: FormatInfo
    filename: str
    output_dir : Path 
    id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=datetime.now)
    
class CancellationToken:
    """A thread-safe flag. UI sets it; worker thread polls it."""
    def __init__(self):
        self._event = Event()
        
    def cancel(self):
        self._event.set()
        
    def is_cancelled(self):
        return self._event.is_set()