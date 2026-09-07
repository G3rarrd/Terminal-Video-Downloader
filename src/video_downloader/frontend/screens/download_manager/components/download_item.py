from uuid import UUID

from textual.reactive import reactive
from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.message import Message
from textual.widget import Widget
from textual.widgets import Button, ListItem, ListView, ProgressBar, Static

from src.video_downloader.frontend.screens.download_manager.formats.formats import format_bytes, format_speed
from src.video_downloader.models.download_job import DownloadJob
from src.video_downloader.models.download_progress import DownloadProgress, JobStatus
from src.video_downloader.service.download_service import DownloadService
from src.video_downloader.utils.conversions import convert_duration, convert_eta

_STATUS_ICONS = {
    JobStatus.QUEUED: "⏸",
    JobStatus.DOWNLOADING: "▶",
    JobStatus.PROCESSING: "⚙",
    JobStatus.COMPLETED: "✓",
    JobStatus.ERROR: "✕",
    JobStatus.CANCELLED: "⊘",
}

_STATUS_COLORS = {
    JobStatus.QUEUED: "dimgrey",
    JobStatus.DOWNLOADING: "cyan",
    JobStatus.PROCESSING: "yellow",
    JobStatus.COMPLETED: "green",
    JobStatus.ERROR: "red",
    JobStatus.CANCELLED: "dimgrey",
}

class DownloadItem(ListItem):
    can_focus = True
    DEFAULT_CSS = """
    DownloadItem {
        height: 3;
        width: 100%;
        border-left: thick $primary;

        layout: horizontal;
        align: center middle;
        padding-left: 1;
        padding-right: 1;
        background: $boost
    }

    DownloadItem > Vertical {
        width: 100%;
        height: 3;
        padding-left: 3;
        padding-right: 3;
    }

    DownloadItem #status-icon {
        width: 1;
        height: 3;
        content-align: center middle;
    }

    DownloadItem #filename {
        width: 100%;
        height: 1;

        text-overflow: ellipsis;
        text-wrap: nowrap;
    }

    DownloadItem #job-progress {
        width: 100%;
        height: 1;
    }
    
    DownloadItem #job-progress Bar{
        width: 100%;
    }

    DownloadItem #progress-info {
        width: 100%;
        height: 1;
    }
    """
    class ProgressUpdated(Message):
        def __init__(self,  progress: DownloadProgress, **kwargs):
            self.progress = progress
            super().__init__()
    
    class Focused(Message):
        def __init__(self, job : DownloadJob) -> None:
            self.job = job
            super().__init__()   



    status: reactive[JobStatus] = reactive(JobStatus.QUEUED)
    downloaded_bytes: reactive[int] = reactive(0)
    total_bytes: reactive[int] = reactive(0)
    speed: reactive[float | None] = reactive(None)
    progress: reactive[float] = reactive(0.0)
    eta : reactive[float] = reactive(0)
    
    def __init__(self, job: DownloadJob, service: DownloadService, **kwargs) -> None:
        super().__init__()
        self.job = job
        self._service = service
        self._unsubscribe = None

    def compose(self) -> ComposeResult:
        yield Static("⏸", id="status-icon")
        yield Vertical(
            Static(self.job.filename, id="filename"),
            ProgressBar(total=100, id="job-progress",  show_eta=False, show_percentage=False),
            Static(f"queued · - · - of - · (-)", id="progress-info")
        )
        
    def on_mount(self) -> None:
        self._unsubscribe = self._service.subscribe_to_job(self.job.id, self._on_progress)
    
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
        self.eta = p.eta or 0
        self.progress = p.progress_pct
        
    def _status_cell(self, status: JobStatus) -> str:
        icon = _STATUS_ICONS.get(status, "?")
        color = _STATUS_COLORS.get(status, "white")
        return f"[{color}]{icon}[/{color}]"

    def watch_status(self, status: JobStatus) -> None:
        eta = convert_eta(self.eta)
        downloaded_bytes = format_bytes(self.downloaded_bytes)
        total_bytes = format_bytes(self.total_bytes)
        status_text = self.status.value
        speed = format_speed(self.speed)
        self.query_one("#status-icon", Static).update(self._status_cell(self.status))
        self.query_one("#progress-info", Static).update(
            f"{status_text} · {eta} · {downloaded_bytes} of {total_bytes} · ({speed})"
        )
        color = _STATUS_COLORS.get(status, "white")
        self.styles.border_left = ("thick", color)   # tuple, not a string
        
    
    def watch_progress(self, pct: float) -> None:
        eta = convert_eta(self.eta)
        downloaded_bytes = format_bytes(self.downloaded_bytes)
        total_bytes = format_bytes(self.total_bytes)
        status = self.status.value
        speed = format_speed(self.speed)
        self.query_one("#job-progress", ProgressBar).update(progress=pct)
        self.query_one("#progress-info", Static).update(
            f"{status} · {eta} · {downloaded_bytes} of {total_bytes} · ({speed})"
        )

