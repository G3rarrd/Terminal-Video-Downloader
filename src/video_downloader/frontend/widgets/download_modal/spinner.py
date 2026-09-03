from textual.app import App, ComposeResult
from textual.widgets import Static
from textual.timer import Timer

class Spinner(Static):
    DEFAULT_CSS = """
        Spinner {
            width: 2;
            height: 2;
        }
    
    """
    
    DEFAULT_FRAMES = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.frame_idx = 0
        self._timer: Timer | None = None
    
    def on_mount(self) -> None:
        self.clear()
        
    def update_spinner(self) -> None:
        self.frame_idx = (self.frame_idx + 1) % len(self.DEFAULT_FRAMES)
        self.update(self.DEFAULT_FRAMES[self.frame_idx])
    
    def load(self):
        self.stop()
        self.frame_idx = 0
        self._timer = self.set_interval(0.05, self.update_spinner)
        self.display = True
        
    def stop(self) -> None:
        if self._timer is not None:
            self._timer.stop()
            self._timer = None
    
    def clear(self) -> None:
        self.stop()
        self.display = False