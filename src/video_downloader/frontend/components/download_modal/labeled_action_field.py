from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.widget import Widget
from textual.widgets import Label, Input, Button

class LabeledActionField(Widget):
    DEFAULT_CSS = """
        LabeledActionField {
                height: auto;        /* 👈 FIX: Prevents widget from collapsing to 0 height */
                width: 100%;
            }
        LabeledActionField Horizontal {
            height: auto;
            align-vertical: middle;
        }
        LabeledActionField Label {
            margin-right: 1;
            width: auto;
        }
        LabeledActionField Input {
            width: 2fr;
        }
        LabeledActionField Button {
            width: auto;
            margin-left: 1;
        }
        """
        
    def __init__(
        self, label: str, placeholder: str, input_id: 
            str, button_label: str | None = None, 
            button_id: str | None = None, **kwargs
        ):
        super().__init__(**kwargs)
        self._label = label
        self._placeholder = placeholder
        self._input_id = input_id
        self._button_label = button_label
        self._button_id = button_id
        
    def compose(self) -> ComposeResult:
        children = [
            Label(self._label),
            Input(placeholder=self._placeholder, id=self._input_id),
        ]
        
        if self._button_label:
            children.append(Button(self._button_label, id=self._button_id))
            
        yield Horizontal(*children)