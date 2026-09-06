from uuid import UUID
from rich.text import Text
from rich.align import Align
from textual.app import ComposeResult
from textual.message import Message
from textual.widget import Widget
from textual.widgets import DataTable, ListItem, ListView
from textual.css.query import NoMatches
from src.video_downloader.frontend.screens.download_manager.formats.formats import format_bytes, format_speed, render_bar
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

def _status_cell(status: JobStatus) -> str:
    icon = _STATUS_ICONS.get(status, "?")
    color = _STATUS_COLORS.get(status, "white")
    return f"[{color}]{icon}[/{color}]"

class DownloadQueue(Widget):
    DEFAULT_CSS = """
    DownloadQueue{
        width: 100%;
        height: 100%;
        border: round $primary;
        padding: 1;
    }
    
    #job-list{
        width: 100%;
        height: 1fr;
    }
    
    ListItem{
        margin-bottom: 1
    }
    ListItem:focus{
        background: $boost;
        border: solid $primary;
    }
    """
    
    
    def __init__(self, service : DownloadService, **kwargs):
        super().__init__()
        self.service = service

    def compose(self) -> ComposeResult:
        yield ListView(id="job-list")

    def add_job(self, job: DownloadJob) -> None:
        list_view = self.query_one("#job-list", ListView)
        list_view.append(ListItem(DownloadItem(job=job, service=self.service), id=f"job-{job.id}"))
        self.service.add_download_job(job)
        
    def on_mount(self) -> None:
        self.border_title = "Downloads"
        
