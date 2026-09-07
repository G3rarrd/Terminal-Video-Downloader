from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID
from .format_info import FormatInfo
from .media_info import MediaInfo
from enum import Enum
from pathlib import Path
from uuid import UUID, uuid4
from PIL import Image as PILImage

from threading import Event
@dataclass(frozen=True)
class DownloadJob:
    format: FormatInfo
    output_dir: Path 
    url: str
    filename: str
    title: str | None
    domain: str | None
    duration: str | None
    thumbnail: PILImage.Image | None
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