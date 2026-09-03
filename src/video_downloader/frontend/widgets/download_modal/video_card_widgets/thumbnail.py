import io
from typing import Optional
from curl_cffi import requests
import httpx
from PIL import Image as PILImage
from textual import work
from textual.app import ComposeResult
from textual.widget import Widget
from textual.widgets import RichLog

from textual_image.widget import Image as TextualImage


class Thumbnail(Widget):
    """A self-contained widget that fetches and displays a thumbnail from a URL."""
    DEFAULT_CSS = """

    Thumbnail {
        width: 100%;
        margin-right: 2;
        height: 100%; 

    }

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
        
    def load(self, thumbnail_url: str) -> None:
        if not thumbnail_url:
            return
        self._fetch_thumbnail(thumbnail_url)
        self.display = True

    @work(thread=True)    
    def _fetch_thumbnail(self, thumbnail_url : str) -> Optional[PILImage.Image]:
        try:
            with requests.Session(impersonate="firefox", timeout=30) as session:
                response = session.get(thumbnail_url)
                response.raise_for_status()
                
                with io.BytesIO(response.content) as buffer:
                    img = PILImage.open(buffer)
                    img.load()
                    
                self.app.call_from_thread(self._on_loaded, img)
                return img
            
        except Exception as exc:
            print(f"Failed to fetch thumbnail: {exc}")

    def _on_loaded(self, pil_img: PILImage.Image) -> None:
        self.query_one("#thumbnail-image", TextualImage).image = pil_img

    def _on_error(self, message: str) -> None:
        self.log.error(f"Thumbnail failed to load: {message}")
        
    def clear(self) -> None:
        self.display = False
        img_widget = self.query_one("#thumbnail-image", TextualImage)
        img_widget.image = None
        img_widget.refresh(layout=True)
        
        