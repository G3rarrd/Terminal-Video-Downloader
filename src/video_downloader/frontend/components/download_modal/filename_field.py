from .input_field_orchestrator import InputFieldOrchestrator
from textual.app import ComposeResult
from textual.message import Message

class FilenameField(InputFieldOrchestrator):
    class Submitted(Message):
        def __init__(self):
            super().__init__()
            
    def __init__(self, **kwargs):
        super().__init__(
            label="FILENAME: ",
            placeholder="(auto-detect)", 
            input_id="filename-input", 
            **kwargs
        )

    def load(self):
        self.display = True
        pass
    
    def on_mount(self):
        self.clear()
    
    def clear(self):
        self.display = False
        pass
    
    