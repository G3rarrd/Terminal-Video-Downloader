from textual.app import App

from src.video_downloader.frontend.messages import JobAdded

from .screens.download_manager.components.download_item import DownloadItem

from .screens.download_modal.download_modal import DownloadModal
from .screens.download_manager.components.download_queue import DownloadQueue
from .screens.download_manager.download_manager import DownloadManagerScreen

from src.video_downloader.models.download_job import DownloadJob
from src.video_downloader.service.download_service import DownloadService

class TerminalVideoDownloadManagerApp(App):
    def __init__(self, service : DownloadService):
        super().__init__()
        self.service = service
        
    DEFAULT_CSS = """
    """

    BINDINGS = [
        ("a", "add_url", "Add Video"),
        ("c", "cancel_download", "Cancel Download")]
    
    def on_mount(self) -> None:
        self.push_screen(DownloadManagerScreen(id="download-screen", service=self.service))
        
    def action_toggle_dark(self) -> None:
        self.theme = ("textual-dark" if self.theme == "textual-light" else "textual-light")
      
    def _on_modal_closed(self, job : DownloadJob) -> None:
        if job is None:
            return
        
        self.screen.post_message(JobAdded(job))
        
    
    def action_cancel_download(self):
        download_screen = self.screen
        
        queue = download_screen.query_one(DownloadQueue)

        queue.cancel_job()
    

    def action_add_url(self):
        self.push_screen(DownloadModal(self.service), self._on_modal_closed)
