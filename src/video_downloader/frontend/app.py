from time import monotonic
from rich.text import Text
from textual import on
from textual.app import App, ComposeResult
from textual.screen import ModalScreen
from textual.binding import Binding
from textual.widgets import DataTable, Footer, Header, Digits, Button, Label, RichLog, Tabs, Tab, Input
from textual.reactive import reactive
from textual.containers import HorizontalGroup, VerticalScroll, Vertical, Grid, Horizontal

from src.video_downloader.frontend.screens.download_manager import DownloadManagerScreen
from src.video_downloader.service.download_service import DownloadService
from src.video_downloader.frontend.screens.download_modal import DownloadModal
class TerminalVideoDownloadManagerApp(App):
    def __init__(self, service : DownloadService):
        super().__init__()
        self.service = service
        
    DEFAULT_CSS = """
    """

    BINDINGS = [("a", "add_url", "Add URL")]
    
    # def compose(self) -> ComposeResult:
    #     yield Vertical(
    #         Footer()
    #     )
    def on_mount(self) -> None:
        self.push_screen(DownloadManagerScreen())
    def action_toggle_dark(self) -> None:
        self.theme = ("textual-dark" if self.theme == "textual-light" else "textual-light")
      
    def on_modal_closed(self, result: bool) -> None:
        # Handles the return value from self.dismiss()
        self.notify(f"Modal dismissed with result: {result}")

    def action_add_url(self):
        self.push_screen(DownloadModal(self.service), self.on_modal_closed)


if __name__ == "__main__":
    app = TerminalVideoDownloadManagerApp()
    app.run()