from textual.reactive import reactive
from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.message import Message
from textual.widget import Widget
from textual.widgets import Button, ListItem, ProgressBar, Static

from src.video_downloader.frontend.formats.formats import format_bytes, format_speed
from src.video_downloader.models.download_job import DownloadJob
from src.video_downloader.models.download_progress import DownloadProgress, JobStatus
from src.video_downloader.service.download_service import DownloadService
from src.video_downloader.utils.conversions import convert_eta

_STATUS_ICONS = {
    JobStatus.QUEUED: "⏸",
    JobStatus.DOWNLOADING: "▶",
    JobStatus.PROCESSING: "⚙",
    JobStatus.COMPLETED: "✓",
    JobStatus.ERROR: "✕",
    JobStatus.CANCELLED: "⊘",
    JobStatus.CANCELLING: "◐",
    JobStatus.STARTING: "◌",
}

_STATUS_COLORS = {
    JobStatus.QUEUED: "dimgrey",
    JobStatus.DOWNLOADING: "cyan",
    JobStatus.PROCESSING: "yellow",
    JobStatus.COMPLETED: "green",
    JobStatus.ERROR: "red",
    JobStatus.CANCELLED: "dimgrey",
    JobStatus.CANCELLING: "orange1",
    JobStatus.STARTING: "cyan",
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

    class Focused(Message):
        def __init__(self, job : DownloadJob) -> None:
            self.job = job
            super().__init__()   




    
    def __init__(self, job: DownloadJob, service: DownloadService, **kwargs) -> None:
        super().__init__()
        self.job = job
        self._service = service
        self._unsubscribe = None
        
        self._latest: DownloadProgress | None = None
        self._rendered_status: JobStatus | None = None  # last status we actually painted
        self._rendered_pct: float | None = None

    def compose(self) -> ComposeResult:
        yield Static("⏸", id="status-icon")
        yield Vertical(
            Static(self.job.filename, id="filename"),
            ProgressBar(total=100, id="job-progress",  show_eta=False, show_percentage=False),
            Static(f"queued · - · - of - · (-)", id="progress-info")
        )
        
    def on_mount(self) -> None:
        # Cache widget references once instead of querying by ID on every update.
        self._status_icon = self.query_one("#status-icon", Static)
        self._progress_bar = self.query_one("#job-progress", ProgressBar)
        self._progress_info = self.query_one("#progress-info", Static)
        
        self._unsubscribe = self._service.subscribe_to_job(self.job.id, self._on_progress)
        self.set_interval(0.25, self._update_display)  # fixed render cadence
    
    def on_unmount(self) -> None:
        if self._unsubscribe:
            self._unsubscribe()

    def _on_progress(self, progress: DownloadProgress) -> None:
        # called from a backend worker thread — post_message is the thread-safe hop
        self._latest = progress
        
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

    def _update_display(self) -> None:
        p = self._latest
        if p is None:
            return  # nothing new since last mount/tick

        pct = p.progress_pct

        # Skip the progress bar + label update if nothing visible actually changed —
        # avoids repainting on sub-percent-point float jitter between fragments.
        pct_changed = self._rendered_pct is None or abs(pct - self._rendered_pct) >= 0.1
        status_changed = p.status != self._rendered_status

        if not pct_changed and not status_changed:
            return

        info_text = (
            f"{p.status.value} · {convert_eta(p.eta or 0)} · "
            f"{format_bytes(p.downloaded_bytes)} of {format_bytes(p.total_bytes)} · "
            f"({format_speed(p.speed)})"
        )
        self._progress_info.update(info_text)  # one write, not two

        if pct_changed:
            self._progress_bar.update(progress=pct)
            self._rendered_pct = pct

        if status_changed:
            self._status_icon.update(self._status_cell(p.status))
            self.styles.border_left = ("thick", _STATUS_COLORS.get(p.status, "white"))
            self._rendered_status = p.status
