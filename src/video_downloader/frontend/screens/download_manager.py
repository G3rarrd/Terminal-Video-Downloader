from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.screen import Screen
from textual.widgets import Footer
from src.video_downloader.frontend.widgets.download_details.job_detail_section import JobDetailSection
from src.video_downloader.frontend.widgets.download_queue.download_queue import DownloadQueue
from src.video_downloader.service.download_service import DownloadService


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
        yield Horizontal(
            DownloadQueue(self.service, id="download-queue"),
            JobDetailSection(self.service, id="job-detail-section"),
        )
        yield Footer()
    
    def on_download_queue_job_highlighted(self, event: DownloadQueue.JobHighlighted) -> None:  # depends on how you signal selection change
        detail_section = self.query_one(JobDetailSection)
        if (event.job):
            detail_section.show_job(event.job)
            
    
    # def on_job_added(self, event: JobAdded) -> None:
    #     """Textual automatically routes 'JobAdded' to 'on_job_added'."""
    #     queue = self.query_one(DownloadQueue)
    #     queue.add_job(event.job)