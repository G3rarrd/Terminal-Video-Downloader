from pathlib import Path
from textual import work
from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.message import Message
from textual.widget import Widget
from textual.widgets import Button, DirectoryTree, Input, Label

from .file_dialog import pick_directory_native

class PathField(Widget):
    """A self-contained widget for browsing and picking a directory path."""
    
    DEFAULT_CSS = """
    PathField {
        height: auto;
        width: 100%;
        margin-top: 1;
    }
    """
    
    def compose(self) -> ComposeResult:
        yield Horizontal(
            Label("Path: "),
            Input(placeholder=str(Path.home()), id="path-input"),
            Button("Browse", id="btn-browse"),
            classes="input-field-row",
        )

    def on_mount(self) -> None:
        self.display = False
        
    def load(self) -> None:
        self.display = True
            
    @work(thread=True)
    def open_native_picker(self) -> None:
        current = self.query_one("#path-input", Input).value
        selected = pick_directory_native(initial_dir=current)
        if selected:
            self.app.call_from_thread(
                setattr, self.query_one("#path-input", Input), "value", selected
            )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-browse":
            self.open_native_picker()

    def clear(self) -> None:
        self.query_one("#path-input", Input).value = ""
        self.display = False