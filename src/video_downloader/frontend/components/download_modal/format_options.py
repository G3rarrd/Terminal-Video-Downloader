from textual.app import ComposeResult
from textual.widget import Widget
from textual.widgets import Select
from textual.message import Message
from src.video_downloader.backend.models.format_info import FormatInfo


class FormatOptions(Widget):

    class FormatSelected(Message):
        def __init__(self, format_info: FormatInfo) -> None:
            self.format_info = format_info
            super().__init__()

    DEFAULT_CSS = """
    FormatOptions {
        height: auto;
        width: 100%;
        margin-top: 1;
    }
    """

    def compose(self) -> ComposeResult:
        yield Select([], id="format-select", prompt="Choose a format...")

    def on_mount(self) -> None:
        self.display = False

    def load(self, video_formats: list[FormatInfo]) -> None:
        if not video_formats:
            self.clear()
            return

        self._formats = video_formats
        options = [
            (self._format_label(fmt), fmt.format_id)
            for fmt in video_formats
        ]

        select = self.query_one(Select)
        select.set_options(options)
        self.display = True

    def _format_label(self, fmt: FormatInfo) -> str:
        size = f"{fmt.filesize / 1_000_000:.1f} MB" if fmt.filesize else "? MB"
        return f"{fmt.resolution or '?'} · {fmt.extension or '?'} · {size}"

    def clear(self) -> None:
        self.query_one(Select).set_options([])
        self._formats = []
        self.display = False

    def on_select_changed(self, event: Select.Changed) -> None:
        if event.value is Select.BLANK:
            return
        selected = next((f for f in self._formats if f.format_id == event.value), None)
        if selected:
            self.post_message(self.FormatSelected(selected))