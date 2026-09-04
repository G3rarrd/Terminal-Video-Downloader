from typing import Optional

from textual.app import ComposeResult
from textual.widget import Widget
from textual.widgets import Select
from textual.message import Message
from src.video_downloader.models.format_info import FormatInfo


class FormatOptions(Widget):
    
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self._formats_by_id: dict[str, FormatInfo] = {}
        

    class FormatSelected(Message):
        def __init__(self, format_info: FormatInfo) -> None:
            self.format_info = format_info
            super().__init__()

    DEFAULT_CSS = """
    FormatOptions {
        height: auto;
        width: 100%;
        margin-bottom: 1;
    }
    """

    def compose(self) -> ComposeResult:
        yield Select([], id="format-select", prompt="Choose a format...")

    @property
    def selected_format(self) -> Optional[FormatInfo]:
        select = self.query_one(Select)
        
        if select.value is Select.BLANK or select.value is None:
            return None
        
        return self._formats_by_id.get(str(select.value), None)

    def on_mount(self) -> None:
        self.display = False

    def load(self, video_formats: list[FormatInfo]) -> None:
        if not video_formats:
            self.clear()
            return
        self._formats = video_formats
        self._formats_by_id = {fmt.format_id: fmt for fmt in video_formats}
        
        options = [
            (self._format_label(fmt), fmt.format_id) for fmt in video_formats
        ]

        select = self.query_one(Select)
        select.set_options(options)
        self.display = True

    def _format_label(self, fmt: FormatInfo) -> str:
        size = f"{fmt.filesize / 1_000_000:.1f} MB" if fmt.filesize else "? MB"
        return f"{fmt.resolution or '?'} · {fmt.video_codec or "?"} · {size} · {fmt.extension or '?'} "

    def clear(self) -> None:
        self.display = False
        self.query_one(Select).set_options([])
        self._formats_by_id.clear()

    def on_select_changed(self, event: Select.Changed) -> None:
        if event.value is Select.BLANK:
            return
        selected = next((f for f in self._formats if f.format_id == event.value), None)
        if selected:
            self.post_message(self.FormatSelected(selected))