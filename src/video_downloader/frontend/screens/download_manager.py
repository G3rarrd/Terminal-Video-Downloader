from textual.app import ComposeResult
from textual.containers import VerticalScroll
from textual.screen import Screen
from textual.widgets import Footer

# from .download_row import DownloadRow

class DownloadManagerScreen(Screen):
    DEFAULT_CSS = (
    """
        DownloadManagerScreen {
            width: 100%;
            height: 100%;
        }
        
        DownloadManagerScreen #download-list{
            border: round $primary;
            width: 100%;
            height: 100%;
        }
    """
    )
    
    
    def __init__(self, **kwargs):
        super().__init__(id="download-screen")
        
    def on_mount(self):
        download_box = self.query_one("#download-list", VerticalScroll)
        download_box.border_title = "Downloads"
        
    def compose(self) -> ComposeResult:
        yield VerticalScroll(id="download-list")
        yield Footer()
        
    def add_job(self, job) -> None:
        download_list = self.query_one("#download-list", VerticalScroll)
        
        # download_list.mount()
        
    # def remove_job(self, job_id) -> None:
    #     try:
    #         row = self.query_one(f"#download-{job_id}")