import base64
from nicegui import ui
from library.colors import colors


class ToggleButton(ui.button):
    def __init__(self, *args, color, sound_path=None, on_click=None, **kwargs):
        super().__init__(*args, **kwargs)
        color_code = colors[color]
        self.style(f'background-color: {color_code} !important; width: 150px; height: 150px;')
        self._on_click = on_click

        if sound_path:
            with open(sound_path, 'rb') as f:
                b64 = base64.b64encode(f.read()).decode()
            ext = sound_path.rsplit('.', 1)[-1]
            self._sound_js = f'new Audio("data:audio/{ext};base64,{b64}").play()'
        else:
            self._sound_js = None

        self.on('click', self.deactivate)

    def deactivate(self) -> None:
        if self._sound_js: ui.run_javascript(self._sound_js)
        self.disable()
        self.style('background-color: gray !important;')
        if self._on_click: self._on_click()

