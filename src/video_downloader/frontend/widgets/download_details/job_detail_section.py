from textual.app import ComposeResult
from textual.containers import VerticalScroll
from textual.widget import Widget

from .details import Details
from src.video_downloader.models.download_job import DownloadJob
from src.video_downloader.service.download_service import DownloadService


class JobDetailSection(Widget):
    DEFAULT_CSS = """
    JobDetailSection {
        layout: vertical;
        height: 100%;
        width: 1fr;
    }
    """

    def __init__(self, service: DownloadService, **kwargs):
        super().__init__(**kwargs)   # was super().__init__() — kwargs were being dropped
        self.service = service

    def compose(self) -> ComposeResult:
        yield VerticalScroll(
            Details(self.service, id="job-details"),
        )

    def show_job(self, job: DownloadJob) -> None:
        """This is called when selection changes."""
        self.query_one("#job-details", Details).update_job(job)