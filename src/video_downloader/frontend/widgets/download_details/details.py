from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widget import Widget
from textual.widgets import Label, Static

from src.video_downloader.frontend.widgets.common.thumbnail import Thumbnail
from src.video_downloader.frontend.widgets.download_details.speed_graph import SpeedGraph
from src.video_downloader.models.download_job import DownloadJob
from src.video_downloader.service.download_service import DownloadService


class Details(Widget):
    """Shows metadata for the currently selected job in the queue."""

    DEFAULT_CSS = """
    Details {
        height: 2fr;
        width: 100%;
        padding: 1 2;
        border: round $primary;
        border-title-align: center;
        border-title-color: $secondary;
    }
    
    Details #thumbnail-detail {
        width: 100%;
        align-horizontal: center;
    }

    Details .detail-row {
        height: auto;
        width: 100%;
    }

    Details .detail-info {
        width: 1fr;
        height: auto;
        text-wrap: wrap;
    }

    Details #title-detail {
        text-style: bold;
        width: 100%;
        height: auto;
        text-wrap: wrap;
        margin-bottom: 1;
        content-align: center middle;
    }

    Details .detail-topic {
        width: 12;
        height: auto;
        color: $text-muted;
    }

    Details .detail-info {
        width: 1fr;
        height: auto;
        text-wrap: wrap;
    }
    """

    _FIELDS = ("url", "domain", "duration", "filename", "output_dir")
    _TOPICS = {
        "url": "URL:",
        "domain": "Domain:",
        "duration": "Duration:",
        "filename": "Filename:",
        "output_dir": "Save to:",
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.current_job: DownloadJob | None = None

    def _detail_row(self, field_name: str) -> Horizontal:
        return Horizontal(
            Label(self._TOPICS[field_name], classes="detail-topic"),
            Label("-", id=f"{field_name}-info", classes="detail-info"),
            classes="detail-row",
        )
    
    def on_mount(self):
        self.border_title = "detail"

    def compose(self) -> ComposeResult:
        yield Thumbnail(id="thumbnail-detail")
        yield Static("Select a job from the downloads", id="title-detail")
        yield Vertical(
            *(self._detail_row(field_name) for field_name in self._FIELDS)
        )

    def update_job(self, job: DownloadJob | None) -> None:
        self.current_job = job

        if job is None:
            self.query_one("#title-detail", Static).update("Select a job from the queue")
            for field_name in self._FIELDS:
                self.query_one(f"#{field_name}-info", Label).update("-")
            return
        
        
        self.query_one("#title-detail", Static).update(job.title or job.filename)
        
        img = self.query_one("#thumbnail-detail", Thumbnail)
        
        img.load(self.current_job.thumbnail)
        
        for field_name in self._FIELDS:
            value = getattr(job, field_name)
            self.query_one(f"#{field_name}-info", Label).update(str(value))