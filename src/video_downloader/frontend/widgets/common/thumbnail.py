import io
from typing import Optional
from curl_cffi import requests
import httpx
from PIL import Image as PILImage
from textual import work
from textual.app import ComposeResult
from textual.widget import Widget
from textual.widgets import RichLog, Static

from textual_image.widget import Image as TextualImage


class Thumbnail(Static):
    """A self-contained widget that fetches and displays a thumbnail from a URL."""
    DEFAULT_CSS = """

    Thumbnail #thumbnail-image {
        width: auto;
        height: auto;
        max-height: 10; 
    }

    """
    def compose(self) -> ComposeResult:
        yield TextualImage(id="thumbnail-image")
        
    def on_mount(self) -> None:
        self.display = False
        
    def load(self, thumbnail : PILImage.Image | None) -> None:
        if not thumbnail:
            return
        self.query_one("#thumbnail-image", TextualImage).image = thumbnail
        self.display = True
        
    def clear(self) -> None:
        self.display = False
        img_widget = self.query_one("#thumbnail-image", TextualImage)
        img_widget.image = None
        img_widget.refresh(layout=True)