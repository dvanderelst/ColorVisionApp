import base64
from nicegui import ui
from library.button_grid import ButtonGrid
from settings import TICK_START_MS, TICK_STEP_MS, TICK_MIN_MS

TICK_SOUND = 'resources/tick.wav'


def _load_b64(path):
    with open(path, 'rb') as f:
        b64 = base64.b64encode(f.read()).decode()
    ext = path.rsplit('.', 1)[-1]
    return b64, ext


def _restart_tick_js(interval_ms):
    return f'''
        clearInterval(window._tickInterval);
        window._tickInterval = setInterval(() => {{
            window._tickAudio.currentTime = 0;
            window._tickAudio.play();
        }}, {interval_ms});
    '''


class Trial:
    def __init__(self, target, colors, cols=3, on_complete=None):
        self._tick_ms = TICK_START_MS

        b64, ext = _load_b64(TICK_SOUND)
        init_audio_js = f'window._tickAudio = new Audio("data:audio/{ext};base64,{b64}");'
        start_tick_js = init_audio_js + _restart_tick_js(TICK_START_MS)
        stop_tick_js  = 'clearInterval(window._tickInterval);'

        def on_error():
            self._tick_ms = max(self._tick_ms - TICK_STEP_MS, TICK_MIN_MS)
            ui.run_javascript(_restart_tick_js(self._tick_ms))

        def complete():
            ui.run_javascript(stop_tick_js)
            if on_complete:
                on_complete()

        ui.run_javascript(start_tick_js)

        with ui.column().classes('mx-auto mt-8 items-center w-fit gap-2'):
            with ui.card().classes('w-full shadow-none border border-gray-300 rounded-xl items-center py-4'):
                ui.label(target.upper()).classes('text-2xl font-bold tracking-widest')

            ButtonGrid(colors, target=target, cols=cols,
                       correct_sound='resources/correct.wav',
                       error_sound='resources/error.wav',
                       on_error=on_error,
                       on_complete=complete)
