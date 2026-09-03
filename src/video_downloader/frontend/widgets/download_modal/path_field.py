from pathlib import Path
from textual import work
from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.message import Message
from textual.widget import Widget
from textual.widgets import Button, DirectoryTree, Input, Label

from .input_field_orchestrator import InputFieldOrchestrator

from .file_dialog import pick_directory_native

DEFAULT_PATH : Path = Path.home()

class PathField(InputFieldOrchestrator):
    """A self-contained widget for browsing and picking a directory path."""
    class Submitted(Message):
        def __init__(self):
            super().__init__()
    
    def __init__(self, **kwargs):
        super().__init__(
            label="PATH: ",
            placeholder=str(DEFAULT_PATH), 
            input_id="path-input",
            button_label="Browse", 
            button_id="btn-browse", 
            **kwargs
        )
    
    def on_mount(self) -> None:
        self.display = False
        
    def load(self) -> None:
        self.display = True
    
    @property
    def default_path(self):
        return DEFAULT_PATH   
       
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