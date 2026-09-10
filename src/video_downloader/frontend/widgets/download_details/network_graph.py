from collections import deque

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Label
from textual_plotext import PlotextPlot
from textual.color import Color
from src.video_downloader.frontend.formats.formats import format_speed, format_bytes
from src.video_downloader.models.download_progress import AggregateProgress
from src.video_downloader.service.download_service import DownloadService

from textual_plotext import PlotextPlot
from textual.color import Color

# Import these from the textual_plotext module where they live
from textual_plotext.plotext_plot import _themes, _rgbify_theme, _sequence


class MyPlotextPlot(PlotextPlot):
    """ Inheriting the PlotextPlot so i can change override the 
    register theme method and alter the content of the plot """
    def _register_theme(self, app_theme_name: str) -> None:
        if self.theme != "auto":
            return

        plotext_theme_name = self._get_plotext_theme_name(app_theme_name)
        theme_variables = self.app.theme_variables

        if plotext_theme_name not in _themes:
            background = Color.parse(
                theme_variables["background"]
            ).rgb
            foreground = Color.parse(
                theme_variables["foreground"]
            ).rgb

            _themes[plotext_theme_name] = _rgbify_theme(
                background,
                background,
                foreground,
                "default",
                _sequence,
            )

        self.refresh()



class NetworkGraph(Horizontal):
    DEFAULT_CSS = """
    NetworkGraph {
        align: center middle;
        height: 1fr;
        width: 100%;
        border: round $primary;
        padding: 1;
        background: $background;
        border-title-color: $secondary;
    }

    #stats {
        height: 100%;
        width: 1fr;
        padding-left: 1;
        align: left middle;
        border: solid grey;
    }

    #stats Label {
        text-style: bold;
        margin-bottom: 1;
    }

    #plot {
        width: 2fr;
        height: 100%;
        background: $panel;
    }
    """
    def __init__(self, service: DownloadService, max_points: int = 30, **kwargs):
        super().__init__(**kwargs)
        self.history: deque[float] = deque([0.0] * max_points, maxlen=max_points)
        self.top_speed: float = 0.0
        self.total_downloaded: float = 0.0
        self.service: DownloadService = service
        self._unsubscribe = None
        self._latest_total_speed: float = 0.0

    def compose(self) -> ComposeResult:
        with Vertical(id="stats"):
            yield Label(f"Speed\n-", id="current-speed")
            yield Label(f"Top speed\n-", id="top-speed")
            yield Label(f"Total\n-", id="total-download")
        yield MyPlotextPlot(id="plot")

    def on_mount(self) -> None:
        self.border_title = "Network Seesion"
        self._unsubscribe = self.service.subscribe_to_total_progress(self._on_total_progress)
        self.set_interval(0.25, self._update_network_graph)
        self._redraw_plot()  # paint the placeholder axes immediately

    def on_unmount(self) -> None:
        if self._unsubscribe:
            self._unsubscribe()

    def _on_total_progress(self, agg: AggregateProgress) -> None:
        # Called from a worker thread — single attribute write, safe without a lock.
        self._latest_total_speed = agg.total_speed
        self.total_downloaded = agg.total_downloaded_bytes

    def _update_network_graph(self) -> None:
        total_speed = self._latest_total_speed
        self.history.append(total_speed)
        self.top_speed = max(self.top_speed, total_speed)
        self._redraw_plot()
        self._update_labels(total_speed)

    def _update_labels(self, current_speed: float) -> None:
        self.query_one("#current-speed", Label).update(
            f"[$text-muted]Speed[/] [$text-secondary]\n{format_speed(current_speed)}[/]"
        )
        self.query_one("#top-speed", Label).update(
            f"[$text-muted]Top speed[/] [$text-secondary]\n{format_speed(self.top_speed)}[/]"
        )
        self.query_one("#total-download", Label).update(
            f"[$text-muted]Total[/] [$text-secondary]\n{format_bytes(self.total_downloaded)}[/]"
        )

    def _redraw_plot(self) -> None:
        plot_widget: PlotextPlot = self.query_one(PlotextPlot)
        plt = plot_widget.plt

        data = list(self.history)
        ymax = max(data) or 1

        n_ticks = 5
        tick_values = [
            round(ymax * i / (n_ticks - 1))
            for i in range(n_ticks)
        ]
        tick_labels = [" " + format_speed(v) + " " for v in tick_values]

        primary = Color.parse(self.app.theme_variables["primary"]).rgb

        plt.clear_data()
        plt.bar(
            range(len(data)),
            data,
            color=primary,
            yside="right",
        )
        plt.xticks([])
        plt.ylim(0, ymax)
        plt.yticks(tick_values, tick_labels, yside="right")
        plt.ticks_color(
            self.app.theme_variables.get("text-muted", "gray")
        )

        plot_widget.refresh()