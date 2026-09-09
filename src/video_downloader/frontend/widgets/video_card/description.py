from textual.app import ComposeResult
from textual.containers import Vertical, VerticalScroll
from textual.widget import Widget
from textual.widgets import Label, Static

from src.video_downloader.models.media_info import MediaInfo
from src.video_downloader.utils.conversions import convert_duration



class Description(VerticalScroll):
    """A self-contained widget that displays video metadata (title, uploader, duration, etc.)."""
    DEFAULT_CSS = """
        Description {
            height: 100%;
            width: 100%;
        }

        Description #desc-body {
            height: auto;
            align-vertical: middle;
        }

        Description #desc-title {
            text-style: bold;
            height: auto;
            width: 100%;
        }

        Description .desc-row {
            height: auto;
            width: 100%;
            color: $text-muted;
        }
        """



    def compose(self) -> ComposeResult:
        yield Static("", id="desc-title")
        yield Label("", id="desc-domain", classes="desc-row")
        yield Label("", id="desc-uploader", classes="desc-row")
        yield Label("", id="desc-duration", classes="desc-row")


    def on_mount(self) -> None:
        self.display = False
        
    # def clear_all(self):
        

    def load(self, metadata : MediaInfo) -> None:
        """Public entry point — call this whenever you have metadata to display."""
        if not metadata:
            self.clear()
            print("Trigger")
            return
        title = metadata.title or "Untitled"
        uploader = metadata.uploader or "Untitled"
        duration = metadata.duration or None
        domain = metadata.domain or "Untitled"
        
        # view_count = metadata.
        self.query_one("#desc-title", Static).update(title)
        
        self.query_one("#desc-uploader", Label).update(
            f"Uploader: " + (uploader if uploader else "?")
        )
        
        self.query_one("#desc-duration", Label).update(
            f"Duration: " + (convert_duration(int(duration)) if duration else "?")
        )
        
        self.query_one("#desc-domain", Label).update(
            f"Domain: " + (domain if domain else "?")
        )
        
        self.display = True


    def clear(self) -> None:
        """Reset all fields to empty — call before a new fetch starts."""
        for widget_id in ("#desc-title", "#desc-uploader", "#desc-domain", "#desc-duration"):
            self.query_one(widget_id).update("")
        self.display = False

