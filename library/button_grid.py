from nicegui import ui
from library.button import ToggleButton


class ButtonGrid:
    def __init__(self, colors, target, cols=3,
                 correct_sound=None, error_sound=None,
                 on_error=None, on_complete=None):

        self._on_complete = on_complete
        self._on_error = on_error
        self._correct_total = colors.count(target)
        self._correct_clicked = 0
        self._total_clicked = 0
        self._total = len(colors)
        self._buttons = []

        self._grid = ui.grid(columns=cols).classes('mx-auto')
        with self._grid:
            for i, color in enumerate(colors):
                is_correct = color == target
                sound = correct_sound if is_correct else error_sound
                btn = ToggleButton('', color=color, sound_path=sound,
                                   on_click=lambda i=i, correct=is_correct: self._handle_click(i, correct))
                self._buttons.append(btn)

    def set_visible(self, visible: bool):
        if visible:
            self._grid.classes(remove='hidden')
        else:
            self._grid.classes('hidden')

    def enable(self):
        for btn in self._buttons:
            btn.enable()

    def disable(self):
        for btn in self._buttons:
            btn.disable()

    def _handle_click(self, index, is_correct):
        self._total_clicked += 1
        if is_correct:
            self._correct_clicked += 1
        elif self._on_error:
            self._on_error()

        all_correct_found = self._correct_clicked == self._correct_total
        all_clicked = self._total_clicked == self._total

        if all_correct_found or all_clicked:
            for btn in self._buttons:
                btn.disable()
                btn.style('background-color: gray !important;')
            if self._on_complete:
                self._on_complete()
