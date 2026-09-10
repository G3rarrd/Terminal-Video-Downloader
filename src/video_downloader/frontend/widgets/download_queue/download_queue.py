from uuid import UUID
from rich.text import Text
from rich.align import Align
from textual.app import ComposeResult
from textual.message import Message
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import DataTable, ListItem, ListView
from textual.css.query import NoMatches
from src.video_downloader.frontend.formats.formats import format_bytes, format_speed, render_bar
from .download_item import DownloadItem

from src.video_downloader.models.download_job import DownloadJob
from src.video_downloader.models.download_progress import DownloadProgress, JobStatus
from src.video_downloader.service.download_service import DownloadService




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

# def _status_cell(status: JobStatus) -> str:
#     icon = _STATUS_ICONS.get(status, "?")
#     color = _STATUS_COLORS.get(status, "white")
#     return f"[{color}]{icon}[/{color}]"

class DownloadQueue(ListView):
    DEFAULT_CSS = """
    DownloadQueue{
        width: 2fr;
        height: 100%;
        border: round $primary;
        border-title-color: $secondary;
        padding: 1;
        background: $surface;
    }
    
    DownloadItem {
        margin: 0 0 1 0;
    }
    """
    
    class JobAdded(Message):
        """Message posted when a new download job is created."""

        def __init__(self, job: DownloadJob) -> None:
            super().__init__()
            self.job = job
            
    class JobHighlighted(Message):
        def __init__(self, job: DownloadJob | None) -> None:
            self.job = job
            super().__init__()

    selected_job: reactive[DownloadJob | None] = reactive(None)
    
    def __init__(self, service : DownloadService, **kwargs):
        super().__init__()
        self.service = service
        self._job_prefix = "job-"

    def add_job(self, job: DownloadJob) -> None:
        self.append(DownloadItem(job=job, service=self.service, id=f"{self._job_prefix}{job.id}") )
        self.service.add_download_job(job)
        self.post_message(self.JobAdded(job))   # posted FROM DownloadQueue itself — bubbles up naturally
    
    def cancel_job(self):
        cur_job = self.selected_job
        
        if not cur_job:
            return
        
        self.service.cancel_job(cur_job.id)
        
    def open_job(self, job: DownloadJob) -> None:
        pass
  
    def on_list_view_highlighted(self, event: ListView.Highlighted) -> None:
        item = event.item
        if isinstance(item, DownloadItem):
            self.selected_job = item.job
            
    def watch_selected_job(self, job: DownloadJob | None) -> None:
        """ Emits a message to the parent on which
            download item or job is currently highlighted
        """
        self.post_message(self.JobHighlighted(job))
        
    def on_mount(self):
        self.border_title = "downloads"
        self.styles.background = self.parent.styles.background
        
        
