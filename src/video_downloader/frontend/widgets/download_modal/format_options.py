from collections import defaultdict
from typing import Optional

from textual.app import ComposeResult
from textual.widget import Widget
from textual.widgets import Select
from textual.message import Message
from src.video_downloader.frontend.formats.format_options_fmt import get_ljust, format_label
from src.video_downloader.models.format_info import FormatInfo


class FormatOptions(Widget):
    
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self._formats_by_video_id: dict[str, FormatInfo] = {}
        self._formats_by_audio_id: dict[str, FormatInfo] = {}
        

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
        yield Select([], id="format-video-select", prompt="Choose a Video format...")
        yield Select([], id="format-audio-select", prompt="Choose an Audio format...")

    @property
    def selected_formats(self) -> tuple[FormatInfo | None, FormatInfo | None] :
        select_video = self.query_one("#format-video-select", Select)
        select_audio = self.query_one("#format-audio-select",Select)
        
        selected_audio = None
        selected_video = None
        if select_video.value is not Select.BLANK and select_video.value is not None:
            selected_video = self._formats_by_video_id.get(str(select_video.value), None)
        
        if select_audio.value is not Select.BLANK and select_audio.value is not None:
            selected_audio = self._formats_by_audio_id.get(str(select_audio.value), None)

        return (selected_video, selected_audio)

    def on_mount(self) -> None:
        self.display = False

    def load(self, video_formats: list[FormatInfo], audio_formats: list[FormatInfo]) -> None:
        
        if video_formats:
            self._video_formats = video_formats
            self._formats_by_video_id = {fmt.format_id: fmt for fmt in video_formats}
            
            video_ljust_map = get_ljust(video_formats)
            video_options = [
                (format_label(fmt, video_ljust_map), fmt.format_id) for fmt in video_formats
            ]
            
            video_select = self.query_one("#format-video-select", Select)
            video_select.set_options(video_options)
            self.query_one("#format-video-select",Select).display = True
            
        
        if audio_formats:
            self._audio_formats = audio_formats
            self._formats_by_audio_id = {fmt.format_id: fmt for fmt in audio_formats}
            
            audio_ljust_map = get_ljust(audio_formats)
            audio_options = [
                (format_label(fmt, audio_ljust_map), fmt.format_id) for fmt in audio_formats
            ]

            audio_select = self.query_one("#format-audio-select", Select)
            audio_select.set_options(audio_options)
            self.query_one("#format-audio-select",Select).display = True
            
        self.display = True
    
    def clear(self) -> None:
        video_select = self.query_one("#format-video-select",Select)
        video_select.set_options([])
        video_select.display = False
        
        audio_select = self.query_one("#format-audio-select",Select)
        audio_select.set_options([])
        audio_select.display = False
        
        self.display = False

    def on_select_changed(self, event: Select.Changed) -> None:
        """Publish the selected format."""

        if event.value in (Select.BLANK, None):
            return

        format_id = str(event.value)

        # Determine which dictionary the event came from.
        if event.select.id == "format-video-select":
            selected =  next((f for f in self._video_formats if f.format_id == event.value), None)
        elif event.select.id == "format-audio-select":
            selected = next((f for f in self._audio_formats if f.format_id == event.value), None)
        else:
            return

        if selected is not None:
            self.post_message(self.FormatSelected(selected))