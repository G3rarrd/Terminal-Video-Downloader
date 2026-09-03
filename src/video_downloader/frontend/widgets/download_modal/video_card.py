from textual.app import ComposeResult
from textual.containers import Grid
from textual.widget import Widget

from src.video_downloader.backend.models.media_info import MediaInfo

from .video_card_widgets.description import Description
from .video_card_widgets.thumbnail import Thumbnail


class VideoCard(Widget):
    DEFAULT_CSS = """
    VideoCard #video-card {
        layout: grid;
        grid-size: 2 1;
        grid-columns: 1fr 3fr;
        grid-rows: auto; 
        height: auto;
        display: none;
        margin-bottom: 1;
    }
    """
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    
    def compose(self) -> ComposeResult:
        yield Grid(
                Thumbnail(id="thumbnail"),
                Description(id="description"),
                id="video-card",
            )
        
    def on_mount(self) -> None:
        self.thumbnail = self.query_one("#thumbnail", Thumbnail)
        self.description = self.query_one("#description", Description)
        
    def load(self, metadata : MediaInfo) -> None:
        self.clear()
        if not metadata:
            return

        thumbnail_img_url = metadata.thumbnail
        self.thumbnail.load(thumbnail_img_url)
        self.description.load(metadata)

        video_card = self.query_one(f"#video-card")
        video_card.display = True
        video_card.refresh(layout=True)
        
    def clear(self):
        widgets : list[Thumbnail | Description]= [ self.thumbnail, self.description]
        
        for w in widgets:
            w.clear()
            
        self.query_one(f"#video-card").display = False
    