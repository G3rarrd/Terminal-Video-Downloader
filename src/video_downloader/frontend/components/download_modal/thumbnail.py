import io
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
        width:100%;
        height: auto;  /* or whatever fits your layout */
    }

    #thumbnail-image {
        width: 100%;
        height: auto;
    }
    """
    def compose(self) -> ComposeResult:
        yield TextualImage(id="thumbnail-image")

    def load(self, thumbnail_url: str) -> None:
        if not thumbnail_url:
            return
        self._fetch(thumbnail_url)

    @work(thread=True)
    def _fetch(self, thumbnail_url: str) -> None:
        try:
            with httpx.Client() as client:
                res = client.get(thumbnail_url)
                res.raise_for_status()
                
        except httpx.HTTPError as e:
            self.app.call_from_thread(self._on_error, str(e))
            return

        pil_img = PILImage.open(io.BytesIO(res.content))
        self.app.call_from_thread(self._on_loaded, pil_img)

    def _on_loaded(self, pil_img: PILImage.Image) -> None:
        self.query_one("#thumbnail-image", TextualImage).image = pil_img

    def _on_error(self, message: str) -> None:
        self.log.error(f"Thumbnail failed to load: {message}")
        # or post a custom message so the parent screen can show it in RichLog