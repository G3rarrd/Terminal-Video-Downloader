from textual.app import App

from .screens.download_manager import DownloadManagerScreen


from .modals.download_modal import DownloadModal
from .widgets.download_queue.download_queue import DownloadQueue


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
        ("c", "cancel_download", "Cancel Download"),
        ("o", "open_download", "Open Download")]
    
    def on_mount(self) -> None:
        self.push_screen(DownloadManagerScreen(id="download-screen", service=self.service))
      
    def _get_download_queue(self) -> DownloadQueue:
        download_screen = self.screen
        return download_screen.query_one(DownloadQueue)
        
    def _on_modal_closed(self, job : DownloadJob) -> None:
        if job is None:
            return

        self._get_download_queue().add_job(job)
    
    def action_cancel_download(self):
        self._get_download_queue().cancel_job()
    
    def action_open_download(self):
        self._get_download_queue().open_job()
        
    def action_add_url(self):
        self.push_screen(DownloadModal(self.service), self._on_modal_closed)
