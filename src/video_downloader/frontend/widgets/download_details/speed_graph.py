from collections import deque

from textual.containers import Vertical
from textual.message import Message
from textual.reactive import reactive
from textual.widgets import Label, Sparkline, Static

from src.video_downloader.frontend.formats.formats import format_speed
from src.video_downloader.models.download_job import DownloadJob
from src.video_downloader.models.download_progress import DownloadProgress
from src.video_downloader.service.download_service import DownloadService

from textual_plot import PlotWidget

class SpeedGraph(Vertical):
    DEFAULT_CSS="""
    SpeedGraph {
        align: center middle;
        height: 1fr;
        border: round $primary;
    }
 
    PlotWidget{
        width: 100%;
        height: 100%;
        margin: 0;
        padding: 0;
        border: round $primary;
    }

    """
    class ProgressListener(Message):
        def __init__(self, progress: DownloadProgress, **kwargs):
            self.progress = progress
            super().__init__(**kwargs)
    
    speed: reactive[float | None] = reactive(None)
    def __init__(self, job: DownloadJob | None, service: DownloadService, max_points: int = 30, **kwargs):
        super().__init__(**kwargs)
        self.history: deque[float] = deque([0.0] * max_points, maxlen=max_points)
        self.service : DownloadService = service
        self.job : DownloadJob | None = job
    
    def compose(self):
        yield PlotWidget(id="plot")
    
    def on_mount(self):
        if self.job is not None:
            self.service.subscribe_to_job(self.job.id,self._on_progress)
        self.border_title = "Speed"
        self._redraw_plot()

    def _on_progress(self, progress: DownloadProgress):
        self.post_message(self.ProgressListener(progress))

    def on_speed_graph_progress_listener(self, event : "SpeedGraph.ProgressListener"):
        self.speed = event.progress.speed
        
    def watch_speed(self) -> None:
        if self.speed is None:
            return
        
        new_value = max(0.0, self.speed)
        self.history.append(new_value / (1024 * 1024))
        
        self._redraw_plot()
        
        # label = self.query_one("#speed-label", Label)
        spd_str : str = format_speed(new_value)
        # label.update(f"Speed: {spd_str}")
        
    def _redraw_plot(self) -> None:
        plot = self.query_one(PlotWidget)

        if not self.history:
            return

        data = list(self.history)

        # Clear previous bars
        plot.clear()

        # X positions
        x = list(range(len(data)))

        # Y-axis: 0 -> next whole MB/s
        max_value = max(data)
        max_y = max(1.0, float(int(max_value) + 1))

        # 0.5 MB/s ticks
        ticks = [
            i * 0.5
            for i in range(int(max_y * 2) + 1)
        ]

        # Draw bars
        plot.bar(
            x=x,
            y=data,
            width=0.8,
            bar_style="cyan",
        )

        # Y-axis range
        plot.set_ylimits(0, max_y)

        # Y-axis ticks
        plot.set_yticks(ticks)

        # Hide X-axis ticks
        plot.set_xticks([])

        # Y-axis label
        plot.set_ylabel("MB/s")

        plot.refresh()