from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.widget import Widget
from textual.widgets import Header, Footer, ListView, ListItem, Label, Static

class JobDetailSection(Widget):
    DEFAULT_CSS = """
    JobDetailSection{
        layout: vertical;
        height: 100%;
        width: 1fr;
    }
    """
    
    def __init__(self, **kwargs):
        super().__init__()
    
    
    
    def compose(self) -> ComposeResult :
        yield VerticalScroll(
            
        )