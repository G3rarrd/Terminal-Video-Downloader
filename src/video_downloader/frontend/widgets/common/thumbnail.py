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
    DEFAULT_CSS = \
    """
    Thumbnail .thumbnail-image {
        width: auto;
        height: auto;
        max-height: 10; 
    }

    """
        
    def on_mount(self) -> None:
        self.display = False

    def load(self, image: PILImage.Image | None) -> None:
        if image is None:
            self.clear()
            return

        self.clear()

        self.mount(
            TextualImage(image, classes="thumbnail-image")
        )

        self.display = True

    def clear(self) -> None:
        for image in self.query(".thumbnail-image"):
            image.remove()

        self.display = False