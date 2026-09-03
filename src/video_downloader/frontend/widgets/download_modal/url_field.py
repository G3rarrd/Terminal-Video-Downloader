from textual.message import Message
from textual.widgets import Button, Input

from .input_field_orchestrator import InputFieldOrchestrator


class URLField(InputFieldOrchestrator):
    class Submitted(Message):
        def __init__(self, url: str) -> None:
            self.url = url
            super().__init__()

    def __init__(self, **kwargs):
        super().__init__(
            label="URL: ",
            placeholder="https://youtube.com", 
            input_id="url-input-field",
            # button_label="Fetch Info",
            # button_id="btn-fetch",
            **kwargs
        )

    def on_input_submitted(self, event: Input.Submitted) -> None:
        print(event.input.id)
        if event.input.id == "url-input-field":
            input_widget = self.query_one("#url-input-field", Input)
            url_text = input_widget.value.strip()

            if not url_text:
                self.post_message(self.Submitted(""))
                return
            self.post_message(self.Submitted(url_text))