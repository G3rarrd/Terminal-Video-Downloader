from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widget import Widget
from textual.widgets import Label, ProgressBar

from models.download_job import DownloadJob


class DownloadItem(Widget):

    def __init__(self, job: DownloadJob):
        super().__init__(
            id=f"download-{job.id}"
        )
        self.job = job

    def compose(self) -> ComposeResult:
        yield Horizontal(
            Label(self.job.filename or "Unknown"),
            Label(self.job.status.value),
        )

        yield ProgressBar(
            total=100,
            show_eta=False,
        )

        yield Horizontal(
            Label("Speed: --"),
            Label("ETA: --"),
        )

    def update_job(self, job: DownloadJob) -> None:
        self.job = job
