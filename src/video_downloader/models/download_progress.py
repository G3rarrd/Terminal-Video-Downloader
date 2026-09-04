from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID
from src.video_downloader.models.format_info import FormatInfo
from src.video_downloader.models.media_info import MediaInfo
from enum import Enum
from pathlib import Path
from uuid import UUID, uuid4

class JobStatus(Enum):
    QUEUED = "queued"
    CANCELLED = "cancelled"
    DOWNLOADING = "downloading"
    FAILED = "failed"
    COMPLETED = "completed"
    PROCESSING = "processing"

@dataclass(frozen=True)
class DownloadProgress:
    job_id: UUID
    status: JobStatus
    progress: float = 0.0
    downloaded_bytes: int = 0
    total_bytes: int = 0
    speed: float | None = None
    eta: int | None = None
    error: str | None = None
    started_at: datetime | None = None
    completed_at: datetime | None = None