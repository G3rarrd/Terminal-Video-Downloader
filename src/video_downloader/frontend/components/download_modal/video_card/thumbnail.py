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
        self._fetch(thumbnail_url)
        self.display = True

    @work(thread=True)
    def _fetch(self, thumbnail_url: str) -> None:
        # 1. Set explicit, generous timeouts for connect and handshake operations
        timeout = httpx.Timeout(connect=15.0, read=15.0, write=15.0, pool=15.0)
        
        # 2. Emulate a standard browser user-agent to avoid CDN rate-limiting/throttling
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        try:
            with httpx.Client(
                timeout=timeout, 
                headers=headers, 
                follow_redirects=True,
                verify=True
            ) as client:
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
        
    def clear(self) -> None:
        self.display = False
        img_widget = self.query_one("#thumbnail-image", TextualImage)
        img_widget.image = None
        img_widget.refresh(layout=True)
        
        