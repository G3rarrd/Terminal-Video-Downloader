from collections import deque

from textual.message import Message
from textual.reactive import reactive
from textual.widgets import Static

from src.video_downloader.models.download_job import DownloadJob
from src.video_downloader.models.download_progress import DownloadProgress
from src.video_downloader.service.download_service import DownloadService
BARS = "▁▂▃▄▅▆▇█"

def make_sparkline(values: list[float]) -> str:
    if not values:
        return ""

    minimum = min(values)
    maximum = max(values)

    if maximum == minimum:
        return BARS[0] * len(values)

    return "".join(
        BARS[
            int((value - minimum) / (maximum - minimum) * (len(BARS) - 1))
        ]
        for value in values
    )

class SpeedGraph(Static):
    DEFAULT_CSS="""
    SpeedGraph.speed-graph {
        width: 100%;
        height: 10;
    }
    """
    
    class ProgressListener(Message):
        def __init__(self, progress: DownloadProgress, **kwargs):
            self.progress = progress
            super().__init__(**kwargs)
    
    speed: reactive[float | None] = reactive(None)
    def __init__(self, job: DownloadJob, service: DownloadService, max_samples: int = 30, **kwargs):
        super().__init__(**kwargs)
        self.samples = deque(maxlen=max_samples)
        self.service = service
        self.job = job
        
    def on_mount(self):
        self.service.subscribe_to_job(self.job.id,self._on_progress)
    
    def _on_progress(self, progress: DownloadProgress):
        self.post_message(self.ProgressListener(progress))

    def on_speed_graph_progress_listener(self, event : "SpeedGraph.ProgressListener"):
        self.speed = event.progress.speed
        
    def watch_speed(self) -> None:
        if self.speed is None:
            return
        
        self.samples.append(self.speed)
        self.update(make_sparkline(list(self.samples)))
