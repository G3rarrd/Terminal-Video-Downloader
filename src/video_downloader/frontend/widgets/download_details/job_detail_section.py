from textual.app import ComposeResult
from textual.containers import Vertical, VerticalScroll
from textual.widget import Widget
from textual.widgets import ContentSwitcher

from src.video_downloader.frontend.widgets.download_details.network_graph import NetworkGraph
from src.video_downloader.frontend.widgets.download_details.speed_graph import SpeedGraph

from .details import Details
from src.video_downloader.models.download_job import DownloadJob
from src.video_downloader.service.download_service import DownloadService


class JobDetailSection(Vertical):
    DEFAULT_CSS = """
    JobDetailSection {
        layout: vertical;
        height: 100%;
        width: 1fr;
        
    }
    
    JobDetailSection > ContentSwitcher{
        height: 1fr;
    }
    """
    
    EMPTY_ID = "speed-graph-empty"

    def __init__(self, service: DownloadService, **kwargs):
        super().__init__(**kwargs)   # was super().__init__() — kwargs were being dropped
        self.service = service

    def compose(self) -> ComposeResult:
        yield Details( id="job-details")
        yield NetworkGraph(self.service)
    

    def show_job(self, job: DownloadJob) -> None:
        """This is called when selection changes."""
        
        self.query_one("#job-details", Details).update_job(job)
        
        # if job is None:
        #     return
        
        # switcher = self.query_one("#speed-graph-switcher", ContentSwitcher)
        # graph_id = f"speed-graph-{job.id}"
        
        # # Mount a graph for this job the first time we see it.
        # if switcher.query(f"#{graph_id}"):
        #     pass # already exists, nothing to mount
        # else:
        #     switcher.mount(SpeedGraph(job, self.service, 10, id=graph_id))
        
        # # Switch visibility to this job's graph. The others stay mounted
        # # (and keep updating/tracking state) in the background.
        # switcher.current = graph_id