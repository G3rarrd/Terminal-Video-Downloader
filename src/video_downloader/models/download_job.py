from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID
from .format_info import FormatInfo
from .media_info import MediaInfo
from enum import Enum
from pathlib import Path
from uuid import UUID, uuid4


@dataclass
class DownloadJob:
    url: str
    format: FormatInfo
    filename: str
    output_dir : Path 
    id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=datetime.now)
    
    
    # status: JobStatus = JobStatus.QUEUED

    # progress: float = 0.0
    # download_bytes : int = 0
    # total_bytes : int = 0
    
    # speed: float | None = None
    # eta: int | None = None
    
    # error: str | None = None
    
    # started_at: datetime | None = None
    # completed_at: datetime | None = None
    