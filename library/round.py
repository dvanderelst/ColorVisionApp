import base64
from nicegui import ui
from library.button_grid import ButtonGrid
from settings import (TICK_START_MS, TICK_STEP_MS, TICK_MIN_MS,
                      ROUND_SCORE_START, SCORE_PENALTY_TICK, SCORE_PENALTY_WRONG)

TICK_SOUND      = 'resources/tick.wav'
ROUND_END_SOUND = 'resources/round_end.wav'


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


def _score_color(score):
    if score > 66:
        return 'positive'
    elif score > 33:
        return 'warning'
    return 'negative'


class Round:
    def __init__(self, target, colors, cols=3, on_complete=None,
                 tick_start_ms=TICK_START_MS, tick_min_ms=TICK_MIN_MS):
        self._tick_ms  = tick_start_ms
        self._tick_min = tick_min_ms
        self._score   = ROUND_SCORE_START

        b64, ext = _load_b64(TICK_SOUND)
        init_audio_js = f'window._tickAudio = new Audio("data:audio/{ext};base64,{b64}");'
        start_tick_js = init_audio_js + _restart_tick_js(tick_start_ms)
        stop_tick_js  = 'clearInterval(window._tickInterval);'

        reb64, reext = _load_b64(ROUND_END_SOUND)
        round_end_js = f'new Audio("data:audio/{reext};base64,{reb64}").play();'

        # mutable refs so closures defined before the UI is built can still reach elements
        refs = {}
        timer_ref = {'timer': None}

        def complete():
            if timer_ref['timer']:
                timer_ref['timer'].cancel()
            ui.run_javascript(stop_tick_js)
            if self._score > 0:
                ui.run_javascript(round_end_js)
            if on_complete:
                on_complete(self._score)

        def update_score(new_score):
            self._score = max(0, new_score)
            refs['ring'].value = self._score
            refs['ring'].props(f'color={_score_color(self._score)}')
            if self._score == 0:
                complete()

        def restart_timer(interval_ms):
            if timer_ref['timer']:
                timer_ref['timer'].cancel()
            with ui.context.client.content:
                timer_ref['timer'] = ui.timer(interval_ms / 1000, lambda: update_score(self._score - SCORE_PENALTY_TICK))

        def on_error():
            self._tick_ms = max(self._tick_ms - TICK_STEP_MS, self._tick_min)
            ui.run_javascript(_restart_tick_js(self._tick_ms))
            update_score(self._score - SCORE_PENALTY_WRONG)
            restart_timer(self._tick_ms)

        with ui.column().classes('mx-auto mt-8 items-center w-fit gap-2'):
            refs['ring'] = ui.circular_progress(
                value=ROUND_SCORE_START, min=0, max=ROUND_SCORE_START,
                show_value=True, size='100px',
            ).props(f'color={_score_color(ROUND_SCORE_START)}')

            with ui.card().classes('w-full shadow-none border border-gray-300 rounded-xl items-center py-4'):
                ui.label(target.upper()).classes('text-2xl font-bold tracking-widest')

            ButtonGrid(colors, target=target, cols=cols,
                       correct_sound='resources/correct.wav',
                       error_sound='resources/error.wav',
                       on_error=on_error,
                       on_complete=complete)

        ui.run_javascript(start_tick_js)
        restart_timer(tick_start_ms)
