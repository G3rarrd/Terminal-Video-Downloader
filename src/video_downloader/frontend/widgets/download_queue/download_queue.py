import os
from pathlib import Path
import platform
import subprocess
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
from src.video_downloader.utils.file_utils import start_file
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
    
    DownloadQueue > DownloadItem.-highlight {
        background: $primary 10%;
    }

    DownloadQueue:focus > DownloadItem.-highlight {
        background: $primary 15%;
    }
    """
    
    class JobAdded(Message):
        """Message posted when a new download job is created."""

        def __init__(self, item: DownloadItem) -> None:
            super().__init__()
            self.item = item
    class JobHighlighted(Message):
        """ Message posted when a download item is highlighted """
        def __init__(self, item :DownloadItem | None) -> None:
            self.item = item
            super().__init__()

    selected_job: reactive[DownloadJob | None] = reactive(None)
    selected_item: reactive[DownloadItem |None] = reactive(None)
    
    def __init__(self, service : DownloadService, **kwargs):
        super().__init__()
        self.service = service
        self._job_prefix = "job-"

    def add_job(self, job: DownloadJob) -> None:
        self.append(DownloadItem(job=job, service=self.service, id=f"{self._job_prefix}{job.id}") )
        self.service.add_download_job(job)
        self.post_message(self.JobAdded(job))   # posted FROM DownloadQueue itself — bubbles up naturally
    
    def cancel_job(self):
        if not self.selected_item:
            return
        
        cur_job = self.selected_item.job
        
        if not cur_job:
            return
        
        self.service.cancel_job(cur_job.id)

    def open_job(self) -> None:
        if not self.selected_item:
            self.notify(f"Highlight a completed job to open", severity="warning")
            return

        job = self.selected_item.job
        
        if not job:
            return

        path = job.output_dir / f"{job.filename}.{job.ext}"
        
        if not path.exists():
            self.notify(f"{path} does not exist.", severity="error")
            return
        
        start_file(path)
  
    def on_list_view_highlighted(self, event: ListView.Highlighted) -> None:
        item = event.item
        if isinstance(item, DownloadItem):
            self.selected_item = item

            
    def watch_selected_item(self, item: DownloadItem | None) -> None:
        """ Emits a message to the parent on which
            download item or job is currently highlighted
        """
        self.post_message(self.JobHighlighted(item))
        
    def on_mount(self):
        self.border_title = "Downloads"
        self.styles.background = self.parent.styles.background
        
        
