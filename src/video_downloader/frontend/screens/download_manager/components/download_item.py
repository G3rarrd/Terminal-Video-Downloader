from uuid import UUID

from rich.progress_bar import ProgressBar
from textual.reactive import reactive
from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.message import Message
from textual.widget import Widget
from textual.widgets import Button, Static

from src.video_downloader.frontend.screens.download_manager.formats.formats import format_bytes, format_speed
from src.video_downloader.models.download_job import DownloadJob
from src.video_downloader.models.download_progress import DownloadProgress, JobStatus
from src.video_downloader.service.download_service import DownloadService
from src.video_downloader.utils.conversions import convert_duration

_STATUS_LABELS = {
    JobStatus.QUEUED: "Queued",
    JobStatus.DOWNLOADING: "Downloading",
    JobStatus.PROCESSING: "Processing",
    JobStatus.COMPLETED: "Completed",
    JobStatus.ERROR: "Error",
    JobStatus.CANCELLED: "Cancelled",
}

_STATUS_ICONS = {
    JobStatus.QUEUED: "⏸",
    JobStatus.DOWNLOADING: "▶",
    JobStatus.PROCESSING: "⚙",
    JobStatus.COMPLETED: "✓",
    JobStatus.ERROR: "✕",
    JobStatus.CANCELLED: "⊘",
}

_STATUS_COLORS = {
    JobStatus.QUEUED: "dim",
    JobStatus.DOWNLOADING: "cyan",
    JobStatus.PROCESSING: "yellow",
    JobStatus.COMPLETED: "green",
    JobStatus.ERROR: "red",
    JobStatus.CANCELLED: "dim red",
}

class DownloadItem(Widget):
    DEFAULT_CSS = """
    DownloadItem {
        height: auto;
        padding: 1 2;
        border-left: thick $primary;
    }
    DownloadItem #filename {
        text-overflow: ellipsis;   # ← just works, no manual truncation needed
        text-wrap: nowrap;
        height: 1;
        width: 100%;
    }
    
    DownloadItem #progress-info{
        height: 1;
        width: 100%;
    }
    
    DownloadItem #job-progress{
        height: 1;
        width: 100%;
    }
    """
    class ProgressUpdated(Message):
        def __init__(self,  progress: DownloadProgress, **kwargs):
            self.progress = progress
            super().__init__()
            
    class CancelRequested(Message):
        """Posted when the user clicks Cancel on this row.
        Not used for control flow directly — DownloadQueue owns the actual
        service.cancel_job() call, this just signals intent upward."""
        def __init__(self, job_id: UUID) -> None:
            self.job_id = job_id
            super().__init__()
    
    status: reactive[JobStatus] = reactive(JobStatus.QUEUED.value)
    downloaded_bytes: reactive[int] = reactive(0)
    total_bytes: reactive[int] = reactive(0)
    speed: reactive[float | None] = reactive(None)
    progress_pct: reactive[float] = reactive(0.0)
    eta : reactive[float] = reactive(0.0)
    
    def __init__(self, job: DownloadJob, service: DownloadService, **kwargs) -> None:
        super().__init__(id=f"download-{job.id}", **kwargs)
        self._job = job
        self._service = service
        self._unsubscribe = None

    def compose(self) -> ComposeResult:
        yield Static("⏸", id="status-icon")
        yield Static(self._job.filename, id="filename")
        yield ProgressBar(total=100, id="job-progress",  show_eta=False, show_percentage=False)
        yield Static(f"- · - of - · (-)", id="progress-info")
        
    def on_mount(self) -> None:
        self._unsubscribe = self._service.subscribe_to_job(self._job.id, self._on_progress)
    
    def on_unmount(self) -> None:
        if self._unsubscribe:
            self._unsubscribe()

    def _on_progress(self, progress: DownloadProgress) -> None:
        # called from a backend worker thread — post_message is the thread-safe hop
        self.post_message(self.ProgressUpdated(progress))
        
    def on_download_item_progress_updated(self, event: "DownloadItem.ProgressUpdated") -> None:
        p = event.progress
        self.status = p.status
        self.downloaded_bytes = p.downloaded_bytes
        self.total_bytes = p.total_bytes
        self.speed = p.speed
        self.progress_pct = p.progress_pct
        
    def watch_status(self, status: JobStatus) -> None:
        self.query_one("#job-status", Static).update(_STATUS_LABELS.get(status, status.value))
        # cancel_btn = self.query_one("#btn-cancel", Button)
        # cancel_btn.disabled = status in (
        #     JobStatus.COMPLETED, JobStatus.ERROR, JobStatus.CANCELLED,
        # )
        pass
    def _status_cell(status: JobStatus) -> str:
        icon = _STATUS_ICONS.get(status, "?")
        color = _STATUS_COLORS.get(status, "white")
        return f"[{color}]{icon}[/{color}]"

    def watch_progress_pct(self, pct: float) -> None:
        eta = convert_duration(self.eta)
        downloaded_bytes = format_bytes(self.downloaded_bytes)
        total_bytes = format_bytes(self.total_bytes)
    
        speed = format_speed(self.speed)
        self.query_one("#status-icon", Static).update(self._status_cell(self.status))
        self.query_one("#job-progress", ProgressBar).update(progress=pct)
        self.query_one("#progress-info", Static).update(f"{eta} · {downloaded_bytes} of {total_bytes} · ({speed})")




    