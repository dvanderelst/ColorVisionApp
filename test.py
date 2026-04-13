import base64
from nicegui import ui
from library.utils import sample_colors
from library.colors import colors as color_map
from settings import TICK_START_MS, TICK_STEP_MS, TICK_MIN_MS

TICK_SOUND = 'resources/tick.wav'
CORRECT_SOUND = 'resources/correct.wav'
ERROR_SOUND = 'resources/error.wav'

def load_b64(path):
    with open(path, 'rb') as f:
        b64 = base64.b64encode(f.read()).decode()
    ext = path.rsplit('.', 1)[-1]
    return b64, ext


@ui.page('/')
def landing():
    with ui.column().classes('mx-auto mt-16 items-center gap-4'):
        ui.label('Color Vision Test').classes('text-3xl font-bold')
        ui.button('Start', on_click=lambda: ui.navigate.to('/trial')).classes('text-lg px-8 py-4')


@ui.page('/trial')
def trial():
    target = 'green'
    button_colors = sample_colors(9, target)

    tick_b64, tick_ext   = load_b64(TICK_SOUND)
    cor_b64,  cor_ext    = load_b64(CORRECT_SOUND)
    err_b64,  err_ext    = load_b64(ERROR_SOUND)

    start_tick_js = f'''
        window._tickAudio = new Audio("data:audio/{tick_ext};base64,{tick_b64}");
        window._tickInterval = setInterval(() => {{
            window._tickAudio.currentTime = 0;
            window._tickAudio.play();
        }}, {TICK_START_MS});
    '''
    stop_tick_js = 'clearInterval(window._tickInterval);'

    correct_js = f'new Audio("data:audio/{cor_ext};base64,{cor_b64}").play()'
    error_js   = f'new Audio("data:audio/{err_ext};base64,{err_b64}").play()'

    ui.run_javascript(start_tick_js)

    correct_total = button_colors.count(target)
    state = {'correct': 0, 'total': 0, 'tick_ms': TICK_START_MS}
    buttons = []

    def handle_click(btn, is_correct):
        btn.disable()
        btn.style('background-color: gray !important;')
        state['total'] += 1
        if is_correct:
            state['correct'] += 1
            ui.run_javascript(correct_js)
        else:
            state['tick_ms'] = max(state['tick_ms'] - TICK_STEP_MS, TICK_MIN_MS)
            ui.run_javascript(error_js)
            ui.run_javascript(f'''
                clearInterval(window._tickInterval);
                window._tickInterval = setInterval(() => {{
                    window._tickAudio.currentTime = 0;
                    window._tickAudio.play();
                }}, {state['tick_ms']});
            ''')

        if state['correct'] == correct_total or state['total'] == len(button_colors):
            for b in buttons:
                b.disable()
                b.style('background-color: gray !important;')
            ui.run_javascript(stop_tick_js)
            ui.notify('Trial complete!')

    with ui.column().classes('mx-auto mt-8 items-center w-fit gap-2'):
        with ui.card().classes('w-full shadow-none border border-gray-300 rounded-xl items-center py-4'):
            ui.label(target.upper()).classes('text-2xl font-bold tracking-widest')

        with ui.grid(columns=3).classes('mx-auto'):
            for color in button_colors:
                hex_color = color_map[color]
                is_correct = color == target
                btn = ui.button('').style(
                    f'background-color: {hex_color} !important; width: 150px; height: 150px;')
                btn.on('click', lambda b=btn, c=is_correct: handle_click(b, c))
                buttons.append(btn)


ui.run()
