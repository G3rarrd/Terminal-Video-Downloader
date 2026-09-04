from pathlib import Path
from textual import on, work
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import Footer, RichLog, Static, Button
import traceback

from src.video_downloader.service.download_service import DownloadService
from src.video_downloader.models.format_info import FormatInfo
from src.video_downloader.models.media_info import MediaInfo
from src.video_downloader.utils.clean_filename import clean_filename

from ...models.download_requests import DownloadRequests
from ..widgets.download_modal.spinner import Spinner
from ..widgets.download_modal.video_card import VideoCard
from ..widgets.download_modal.filename_field import FilenameField
from ..widgets.download_modal.format_options import FormatOptions
from ..widgets.download_modal.path_field import PathField
from ..widgets.download_modal.url_field import URLField


class DownloadModal(ModalScreen[bool]):
    """A modal popup to view detailed download info."""

    DEFAULT_CSS = """
    DownloadModal {
        align: center middle;
    }

    #modal-container {
        max-width: 70;
        height: auto;
        border: round $primary;
        border-title-align: left;
        border-title-color: $text;
        border-title-background: $surface;
        background: $surface;
        margin: 1 2;
        padding: 0 2;
        padding-top: 1;
    }
    
    #video-card {
        height: auto;
    }
    
    #format-options {
        height: auto;
    }
    
    #path-selector {
        height: auto;
    }
    
    #url-field {
        width: 1fr;
    }
    
    #url-row {
        height: auto;
    }
    
    
    #spinner {
        width: 1;
        height: 100%;              
        content-align-vertical: middle;
    }
    
    Footer {
        width: 100%;
        height: auto;
        margin-bottom: 0;
        background: transparent;
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
        Binding(key="escape", action="close_modal", description="cancel"),
    ]
    
    def __init__(self, service : DownloadService, **kwargs):

        super().__init__()
        
        self.service = service

        self.media_info: MediaInfo | None = None
        self._is_fetching: bool = False

    def compose(self) -> ComposeResult:
        yield Vertical(
            Horizontal(URLField(id="url-field"), Spinner(id="spinner"), id="url-row"),
            VideoCard(id="video-card"),
            FormatOptions(id="format-options"),
            PathField(id="path-selector"),
            FilenameField(id="filename-field"),
            Button("Add Download", id="download-btn"),
            Static("[b]enter[/b] confirm/next   [b]tab[/b] next   [b]esc[/b] cancel", id="hint-bar"),
            id="modal-container",
        )
        
    def _load_download_btn(self):
        self.query_one("#download-btn", Button).display = True
        
    def _clear_download_btn(self):
        self.query_one("#download-btn", Button).display = False
        
    def on_mount(self) -> None:
        widget = self.query_one("#modal-container")
        widget.border_title = "Add Download"
        self._clear_download_btn()
        
    def _reset(self) -> None:
        for selector, widget_type in (
            ("#video-card", VideoCard),
            ("#format-options", FormatOptions),
            ("#path-selector", PathField),
            ("#filename-field", FilenameField),
        ):
            self.query_one(selector, widget_type).clear()
            
        self._clear_download_btn()

    @work(thread=True)
    def fetch_metadata(self, url_text: str) -> None:
        self._is_fetching = True
        
        spinner = self.query_one("#spinner", Spinner)
        
        self.app.call_from_thread(spinner.load)
        try:

            metadata = self.service.extract_metadata(url_text)

            self.media_info = metadata.media
            
            video_formats : list[FormatInfo] = metadata.video_formats

            self.app.call_from_thread(lambda: self.notify(f"[green]Got metadata:[/green] {self.media_info.title}"))

            video_card = self.query_one("#video-card", VideoCard)
            self.app.call_from_thread(video_card.load, self.media_info)

            format_options = self.query_one("#format-options", FormatOptions)
            self.app.call_from_thread(format_options.load, video_formats)

            path_field = self.query_one("#path-selector", PathField)
            self.app.call_from_thread(path_field.load)
            
            filename_field = self.query_one("#filename-field", FilenameField)
            self.app.call_from_thread(filename_field.load)
            
            self.app.call_from_thread(self._load_download_btn)
            
        except Exception:
            self.app.call_from_thread(lambda: self.notify(f"[bold red]Failed to fetch URL:[/bold red] {traceback.format_exc()}"))
            
        finally:
            self._is_fetching = False
            self.app.call_from_thread(spinner.clear)

    @on(URLField.Submitted)
    def on_url_field_submitted(self, event: URLField.Submitted) -> None:
        event.stop()
        
        if self._is_fetching:
            return

        if not event.url:
            self.notify("URL cannot be empty", severity="error")
            return

        self._reset()
        
        self.notify(f"[green]Fetching URL info for:[/green] {event.url}")
        
        self.fetch_metadata(event.url)
        
        
    @on(Button.Pressed, "#download-btn")
    def on_download_pressed(self, event: Button.Pressed) -> None:
        event.stop()

        format_options = self.query_one("#format-options", FormatOptions)
        filename_field = self.query_one("#filename-field", FilenameField)
        path_field = self.query_one("#path-selector", PathField)
        
        url = self.media_info.webpage_url
        title = self.media_info.title
        
        selected_format = format_options.selected_format
        filename = filename_field.value
        output_dir = path_field.value
        
        if not output_dir:
            output_dir = path_field.default_path
        
        if not filename:
            filename = clean_filename(title)
        
        if not selected_format:
            self.notify("Please select a video format!", severity="error")
            return
        
        request = DownloadRequests(
            url=url,
            format=selected_format,
            filename=clean_filename(filename),
            output_dir=Path(output_dir)
        )
        
        self.notify(f"Starting download: {url}")
        
        self.service.add_download_job(request)

    def action_close_modal(self) -> None:
        self.dismiss(True)