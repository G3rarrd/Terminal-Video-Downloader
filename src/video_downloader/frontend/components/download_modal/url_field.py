from textual.message import Message
from textual.widgets import Button, Input

from .labeled_action_field import LabeledActionField


class URLField(LabeledActionField):
    class Submitted(Message):
        def __init__(self, url: str) -> None:
            self.url = url
            super().__init__()

    def __init__(self, **kwargs):
        super().__init__(
            label="URL: ",
            placeholder="https://youtube.com", 
            input_id="url-input-field",  # Distinct ID for child Input
            button_label="Fetch Info", 
            button_id="btn-fetch", 
            **kwargs
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        
        if event.button.id == "btn-fetch":
            input_widget = self.query_one("#url-input-field", Input)
            url_text = input_widget.value.strip()

            if not url_text:
                print("Message Failed")
                self.post_message(self.Submitted(""))
                return
            
            print("message posted")
            self.post_message(self.Submitted(url_text))