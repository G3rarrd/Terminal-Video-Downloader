from pathlib import Path
from textual import on, work
from textual.app import ComposeResult
from textual.containers import Vertical
from textual.screen import ModalScreen
from textual.widgets import RichLog

from src.video_downloader.backend.yt_dlp.format_orchestrator import FormatOrchestrator

from .format_options import FormatOptions
from .path_field import PathField
from .url_field import URLField
from .video_card.video_card import VideoCard


class DownloadModal(ModalScreen[bool]):
    """A modal popup to view detailed download info."""

    DEFAULT_CSS = """
    DownloadModal {
        align: center middle;
    }

    #modal-container {
        max-width: 70;
        height: auto;
        border: solid $primary;
        background: $surface;
        padding: 1 2;
        margin: 1 2;
    }

    .input-field-row {
        height: auto;
        align-vertical: middle;
    }

    .input-field-row Label {
        margin-right: 1;
        height: 100%;
        content-align-vertical: middle;
        width: auto;
    }
    
    .input-field-row Input {
        width: 1fr;
    }
    
    .input-field-row Button {
        width: auto;
        margin-left: 1;
    }

    #log-pane {
        dock: top;
        width: 100%;
        height: 1;
        padding: 0 1;
        background: $panel;
    }
    """

    BINDINGS = [
        ("escape", "close_modal", "Cancel"),
    ]

    def compose(self) -> ComposeResult:
        yield RichLog(id="log-pane")
        yield Vertical(
            URLField(id="url-field"),
            VideoCard(id="video-card"),
            FormatOptions(id="format-options"),
            PathField(id="path-selector"),
            id="modal-container",
        )

    def _reset(self) -> None:
        for selector, widget_type in (
            ("#video-card", VideoCard),
            ("#format-options", FormatOptions),
        ):
            self.query_one(selector, widget_type).clear()

    @work(thread=True)
    def fetch_and_show(self, url_text: str) -> None:
        log = self.query_one("#log-pane", RichLog)

        try:
            data_extractor = FormatOrchestrator()
            data = data_extractor.inspect_url(url_text)
            metadata = data.media
            video_formats = data.video_formats
            
            self.app.call_from_thread(lambda: log.write(f"[green]Got metadata:[/green] {metadata}"))

            video_card = self.query_one("#video-card", VideoCard)
            self.app.call_from_thread(video_card.load, metadata)

            format_options = self.query_one("#format-options", FormatOptions)
            self.app.call_from_thread(format_options.load, video_formats)
            
        except Exception as exc:
            self.app.call_from_thread(
                lambda: log.write(f"[bold red]Failed to fetch URL:[/bold red] {exc}")
            )
    @on(URLField.Submitted)
    def on_url_field_submitted(self, event: URLField.Submitted) -> None:
        print("message Recieved")
        log = self.query_one("#log-pane", RichLog)

        if not event.url:
            log.write("[bold red]Error:[/bold red] URL field is empty!")
            return

        self._reset()
        log.write(f"[green]Fetching URL info for:[/green] {event.url}")
        self.fetch_and_show(event.url)

    def action_close_modal(self) -> None:
        self.dismiss(True)