import io

import httpx
from textual import work
from textual.app import ComposeResult
from textual.containers import Grid, Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, DataTable, Input, Label, RichLog

from src.video_downloader.backend.yt_dlp.extractor import YtDlpExtractor
from src.video_downloader.frontend.components.download_modal.thumbnail import Thumbnail


class DownloadModal(ModalScreen[bool]):
    """A modal popup to view detailed download info."""

    DEFAULT_CSS = """
    DownloadModal {
        align: center middle;
    }

    #modal-container {
        width: 60;
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
        width: 1fr;   /* takes remaining space, but shares it with the button */
    }
    
    .input-field-row Button {
        width: auto;
        margin-left: 1;
    }

    #thumbnail {
        width: 100%;
        height: auto;
        margin: 1 0;
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

    def input_field(self, label_name: str, placeholder: str, id: str):
        return Horizontal(
            Label(label_name),
            Input(placeholder=placeholder, id=id),
            classes="input-field-row",
        )

    def url_input(self):
        return Horizontal(
            Label("URL: "),
            Input(placeholder="https://youtube.com", id="url-input"),
            Button("Fetch Info", variant="primary", id="btn-fetch"),
            classes="input-field-row",
        )

    def compose(self) -> ComposeResult:
        yield RichLog(id="log-pane")
        yield Vertical(
            self.url_input(),
            Thumbnail(id="thumbnail"),
            id="modal-container",
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-fetch":
            input_widget = self.query_one("#url-input", Input)
            url_text = input_widget.value.strip()
            log = self.query_one("#log-pane", RichLog)

            if not url_text:
                log.write("[bold red]Error:[/bold red] URL field is empty!")
                return

            log.write(f"[green]Fetching URL info for:[/green] {url_text}")
            self.fetch_and_show(url_text)

    @work(thread=True)
    def fetch_and_show(self, url_text: str) -> None:
        extractor = YtDlpExtractor()
        metadata = extractor.extract_metadata(url_text)

        log = self.query_one("#log-pane", RichLog)
        self.app.call_from_thread(lambda: log.write(f"[green]Got metadata:[/green] {metadata}"))

        thumbnail = self.query_one("#thumbnail", Thumbnail)
        self.app.call_from_thread(thumbnail.load, metadata.thumbnail)

    def action_close_modal(self):
        self.dismiss(True)