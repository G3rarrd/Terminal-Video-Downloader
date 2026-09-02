from time import monotonic
from rich.text import Text
from textual import on
from textual.app import App, ComposeResult
from textual.screen import ModalScreen
from textual.binding import Binding
from textual.widgets import DataTable, Footer, Header, Digits, Button, Label, RichLog, Tabs, Tab, Input
from textual.reactive import reactive
from textual.containers import HorizontalGroup, VerticalScroll, Vertical, Grid, Horizontal

from .components.download_modal.download_modal import DownloadModal


class TerminalVideoDownloadManager(App):
    CSS = """

        """

    BINDINGS = [
            ("a", "add_url", "Add URL"),
        ]
    
    def compose(self) -> ComposeResult:
        yield Footer()
        
    def action_toggle_dark(self) -> None:
        self.theme = ("textual-dark" if self.theme == "textual-light" else "textual-light")
      
    def on_modal_closed(self, result: bool) -> None:
        # Handles the return value from self.dismiss()
        self.notify(f"Modal dismissed with result: {result}")

        
    def action_add_url(self):
        self.push_screen(DownloadModal(), self.on_modal_closed)
        
    # def action_add_download_modal(self)-> None:
    #     def on_modal_close(result : dict | None) -> None:
    #         if result:
    #             self.notify(f"Starting download: {result['url']}")
    #         else:
    #             self.notify("Cancelled", severity="warning")
            
    #     self.push_screen(DownloadModal(), on_modal_close)
        
    # def action_append_download(self):
    #     container = self.query_one("#container")
    #     container.mount( Label("First"), Label("Second"), Button("Click me"))

app = TerminalVideoDownloadManager()
if __name__ == "__main__":
    app.run()