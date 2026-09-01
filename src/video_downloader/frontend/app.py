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

TAB_NAMES = [
    "Download",
    "Settings"
]

# class DownloadModal(ModalScreen[dict | None]):
#     DEFAULT_CSS = """
#     AddDownloadModal {
#         align: center middle;
#     }

#     #dialog {
#         grid-size: 2;
#         grid-gutter: 1;
#         padding: 1 2;
#         width: 70;
#         height: 17;
#         border: thick $background 80%;
#         background: $surface;
#     }

#     .field-label {
#         column-span: 2;
#         margin-top: 1;
#     }

#     Input {
#         column-span: 2;
#     }

#     #connections-input {
#         column-span: 1;
#     }

#     Button {
#         width: 100%;
#         margin-top: 1;
#     }
#     """
#     def compose(self) -> ComposeResult:
#         yield Grid(
#             Label("URL or Magnet Link:", classes="field-label"),
#             Input(
#                 placeholder="https://example.com/file.iso",
#                 id="url-input",
#             ),
#             Label("Save Destination Path:", classes="field-label"),
#             Input(
#                 placeholder="/home/user/Downloads",
#                 value="/home/user/Downloads",
#                 id="path-input",
#             ),
#             Label("Connections:", classes="field-label"),
#             Input(
#                 value="16",
#                 type="integer",  # Restricts input to numbers only
#                 id="connections-input",
#             ),
#             Button("Start Download", variant="primary", id="submit"),
#             Button("Cancel", variant="error", id="cancel"),
#             id="dialog",
#         )
        
#     @on(Input.Submitted)
#     def handle_submit(self) -> None:
#         self._confirm_and_close()
        
#     @on(Input.Submitted)
#     def handle_submit(self) -> None:
#         self._confirm_and_close()
        
#     @on(Button.Pressed, "#cancel")
#     def on_cancel_click(self) -> None:
#         self.dismiss(None)
        
#     def _confirm_and_close(self) -> None:
#         url = self.query_one("#url-input", Input).value.strip()
#         path = self.query_one("#path-input", Input).value.strip()
#         connections = self.query_one("#connections-input", Input).value.strip()

#         if url:
#             self.dismiss(
#                 {
#                     "url": url,
#                     "path": path,
#                     "connections": int(connections) if connections else 16,
#                 }
#             )

class TerminalVideoDownloadManager(App):
    CSS = """
    
        Screen {
            layout: vertical;
            background: #1a1b26;
            color: #c0caf5;
        }
        
        DataTable {
            background: #1f2335;
            border: solid #3b4261;
        }
        #toolbar {
            height: 3;
            margin: 1 1;
        }
        
        #downloads-table {
            height: 1fr;
            border: solid green;
        }
        
        #details-pane {
            height: 10;
            margin: 0 1;
        }
        
        
        #log-pane {
            height: 8;
            border: solid blue;
        }
        """

    BINDINGS = [
            ("a", "add_url", "Add URL"),
            ("p", "toggle_pause", "Pause/Resume"),
            ("q", "quit", "Quit"),
        ]
    
    def compose(self) -> ComposeResult:
        yield Header()
        yield Horizontal(
                    Button("Add URL (+a)", variant="success", id="btn-add"),
                    Button("Pause All", id="btn-pause"),
                    Button("Resume All", id="btn-resume"),
                    id="toolbar",
                )
        yield DataTable(id="downloads-table")

        # Metadata & Settings Middle Pane
        yield Horizontal(
            Vertical(
                Label("[bold]Selected Video Details[/bold]"),
                Label("URL: https://..."),
                Label("Format: 1080p (h264)"),
                classes="box",
            ),
            Vertical(
                Label("[bold]Queue Controls[/bold]"),
                Label("Max Concurrent Downloads: 3"),
                Label("Speed Limit: Unlimited"),
                classes="box",
            ),
            id="details-pane",
        )

        # Logs Console
        yield RichLog(id="log-pane", highlight=True, markup=True)
        yield Footer()
        
    def action_toggle_dark(self) -> None:
        self.theme = ("textual-dark" if self.theme == "textual-light" else "textual-light")
      
    def on_tabs_tab_activated(self, event : Tabs.TabActivated) -> None:
        pass
    
    def on_modal_closed(self, result: bool) -> None:
        # Handles the return value from self.dismiss()
        self.notify(f"Modal dismissed with result: {result}")
    
    def on_mount(self) -> None:
        table = self.query_one(DataTable)
        table.add_columns(
            "ID", "Title", "Quality", "Size", "Speed", "ETA", "Progress", "Status"
        )
        table.add_row(
            "#1",
            "Lecture_01.mp4",
            "1080p",
            "450 MB",
            "4.2 MB/s",
            "00:45",
            "45%",
            "Downloading",
        )
        table.add_row(
            "#2",
            "Synthwave_Mix.mkv",
            "4K",
            "1.2 GB",
            "8.1 MB/s",
            "01:12",
            "88%",
            "Downloading",
        )
        
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