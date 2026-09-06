from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Footer

from src.video_downloader.frontend.messages import JobAdded
from src.video_downloader.service.download_service import DownloadService

from .components.download_queue import DownloadQueue

# from .download_row import DownloadRow

class DownloadManagerScreen(Screen):
    DEFAULT_CSS = (
    """
        DownloadManagerScreen {
            width: 100%;
            height: 100%;
        }
    """
    )

    def __init__(self, service : DownloadService, **kwargs):
        super().__init__(id="download-screen")
        self.service = service

    def compose(self) -> ComposeResult:
        yield DownloadQueue(service=self.service)
        yield Footer()
        
    
    def on_job_added(self, event: JobAdded) -> None:
        """Textual automatically routes 'JobAdded' to 'on_job_added'."""
        queue = self.query_one(DownloadQueue)
        queue.add_job(event.job)