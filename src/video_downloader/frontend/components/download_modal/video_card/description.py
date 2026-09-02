from textual.app import ComposeResult
from textual.containers import Vertical, VerticalScroll
from textual.widget import Widget
from textual.widgets import Label, Static

from src.video_downloader.backend.models.media_info import MediaInfo



class Description(Widget):
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
        yield VerticalScroll(
            Static("", id="desc-title"),
            Label("", id="desc-uploader", classes="desc-row"),
            Label("", id="desc-duration", classes="desc-row"),

            id="desc-body",
        )
        
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
        # view_count = metadata.

        self.query_one("#desc-title", Static).update(title)
        self.query_one("#desc-uploader", Label).update(
            f"Uploader: " + (uploader if uploader else "?")
        )
        self.query_one("#desc-duration", Label).update(
            f"Duration: " + (self._convert_duration(duration) if  duration else "?")
        )
        self.display = True
        # self.query_one("#desc-views", Label).update(
        #     f"Views: {view_count:,}" if view_count else ""
        # )
        
    def _convert_duration(self, duration: int) -> str:
        hours, remainder = divmod(duration, 3600)
        minutes, seconds = divmod(remainder, 60)

        parts = [hours, minutes, seconds]
        while len(parts) > 1 and parts[0] == 0:
            parts.pop(0)

        return ":".join(f"{p:02d}" for p in parts)

    def clear(self) -> None:
        """Reset all fields to empty — call before a new fetch starts."""
        for widget_id in ("#desc-title", "#desc-uploader", "#desc-duration"):
            self.query_one(widget_id).update("")
        self.display = False

