import asyncio
import os
import random
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

from nicegui import ui, app
from library.utils import sample_colors
from library.round import Round
from library.colors import colors as COLOR_HEX
from settings import N_ROUNDS, DIFFICULTY, TIMEZONE, DASHBOARD_PASSWORD
import db

app.on_startup(db.setup)
app.add_static_files('/resources', 'resources')

ui.add_css('''
    body, .q-page { background-color: black !important; }
    .q-radio__label { color: white !important; }
''', shared=True)

COLORS = ['red', 'green', 'blue', 'yellow', 'magenta', 'cyan']


@ui.page('/')
def landing():
    with ui.column().classes('mx-auto mt-12 gap-6 w-full max-w-2xl px-8'):

        with ui.column().classes('gap-3'):
            ui.label('Instructions').classes('text-white font-bold text-lg')
            for text in [
                'Please wear your goggles while playing this game.',
                'When starting the game, you will see nine boxes of different primary or '
                'secondary colors. Above those boxes is a word indicating the color of the '
                'box to be identified. All boxes of that color must be selected.',
                'The faster your group selects all boxes, the higher your final score.',
                f'You have a limited number of seconds per screen, with {N_ROUNDS} total '
                f'screens. The amount of time available depends on the setting you choose below.',
                'An incorrect answer (selecting the incorrectly colored box) incurs a penalty '
                'as the speed of the game increases.',
            ]:
                ui.label(text).classes('text-gray-300 text-sm leading-relaxed')

        with ui.row().classes('items-center gap-12 mt-2'):
            ui.label('Difficulty Setting:').classes('text-white')
            difficulty = ui.radio(
                ['Easy', 'Medium', 'Hard'], value='Easy',
            ).props('inline dark')

        with ui.row().classes('self-center gap-4 mt-2'):
            ui.button(
                'START',
                on_click=lambda: ui.navigate.to(f'/game/{difficulty.value.lower()}'),
            ).classes('text-lg font-bold px-10 py-3').props('flat color=red')
            ui.button(
                'TRAIN',
                on_click=lambda: ui.navigate.to('/train'),
            ).classes('text-lg font-bold px-10 py-3').props('flat color=white')

        ui.link('Instructor Dashboard', '/dashboard').classes('self-center text-gray-500 text-xs mt-4')


@ui.page('/game/{difficulty}')
def game(difficulty: str):
    tick_cfg = DIFFICULTY.get(difficulty, DIFFICULTY['medium'])
    state = {'round_num': 0, 'total_score': 0}
    container = ui.column().classes('w-full')

    def start_round():
        target = random.choice(COLORS)
        colors = sample_colors(9, target)
        container.clear()
        with container:
            ui.label(f'Round {state["round_num"]} / {N_ROUNDS}').classes('text-center text-gray-500 mt-4')
            Round(target, colors, on_complete=next_round,
                  tick_start_ms=tick_cfg['tick_start_ms'],
                  tick_min_ms=tick_cfg['tick_min_ms'])

    def next_round(score=0):
        state['total_score'] += score
        state['round_num'] += 1
        if state['round_num'] > N_ROUNDS:
            multiplier = tick_cfg['multiplier']
            final_score = round(state['total_score'] * multiplier)
            ui.navigate.to(f'/done/{final_score}/{difficulty}')
            return
        container.clear()
        with container:
            with ui.column().classes('mx-auto mt-32 items-center gap-2'):
                ui.label(f'Round {state["round_num"]}').classes('text-5xl font-bold text-gray-300')
                ui.label(f'of {N_ROUNDS}').classes('text-xl text-gray-500')
        with ui.context.client.content:
            ui.timer(1.0, start_round, once=True)

    next_round()


@ui.page('/done/{total_score}/{difficulty}')
def done(total_score: int, difficulty: str):
    multiplier = DIFFICULTY.get(difficulty, DIFFICULTY['medium'])['multiplier']
    max_score = round(N_ROUNDS * 100 * multiplier)

    with ui.column().classes('mx-auto mt-16 items-center gap-4'):
        ui.label('Done!').classes('text-3xl font-bold text-white')
        ui.label(f'{total_score} / {max_score}').classes('text-6xl font-bold text-primary')
        ui.label(f'across {N_ROUNDS} rounds').classes('text-gray-400')

        with ui.row().classes('items-center gap-2 mt-4'):
            team_name = ui.input(placeholder='Team name').classes('w-48').props('dark outlined')
            submit_btn = ui.button('Submit score')

        async def handle_submit():
            if not team_name.value.strip():
                ui.notify('Please enter a team name.', color='warning')
                return
            submit_btn.disable()
            await db.submit(team_name.value.strip(), total_score, max_score, difficulty)
            ui.notify('Score submitted!', color='positive')

        submit_btn.on_click(handle_submit)

        ui.button('Play again', on_click=lambda: ui.navigate.to('/')).classes('mt-2')


@ui.page('/dashboard')
def dashboard():
    tz = ZoneInfo(TIMEZONE)
    container = ui.column().classes('w-full max-w-3xl mx-auto mt-12 px-8 gap-6')

    def show_login():
        with container:
            ui.label('Instructor Dashboard').classes('text-white text-2xl font-bold')
            pwd = ui.input(placeholder='Password', password=True).props('dark outlined')

            async def attempt():
                if pwd.value == DASHBOARD_PASSWORD:
                    container.clear()
                    await show_scores()
                else:
                    ui.notify('Incorrect password', color='negative')

            pwd.on('keydown.enter', attempt)
            ui.button('Login', on_click=attempt)

    async def show_scores():
        today = datetime.now(tz).date()
        # Capture client content reference while slot context is available
        client_content = ui.context.client.content

        with container:
            ui.label('Scores').classes('text-white text-2xl font-bold')
            with ui.row().classes('w-full items-start gap-6'):
                date_picker = ui.date(value=today.isoformat()).props('dark')
                table_container = ui.column().classes('flex-1')
                with table_container:
                    ui.label('Getting data...').classes('text-gray-400')

        async def refresh():
            raw = date_picker.value
            if not raw:
                return
            selected = date.fromisoformat(raw.replace('/', '-'))
            start = datetime(selected.year, selected.month, selected.day, tzinfo=tz)
            end = start + timedelta(days=1)
            rows = await db.get_scores(start, end)

            table_container.clear()
            with table_container:
                if not rows:
                    ui.label('No submissions for this date.').classes('text-gray-400')
                else:
                    columns = [
                        {'name': 'rank',       'label': '#',          'field': 'rank',       'align': 'left'},
                        {'name': 'team',       'label': 'Team',       'field': 'team',       'align': 'left'},
                        {'name': 'score',      'label': 'Score',      'field': 'score',      'align': 'left'},
                        {'name': 'max_score',  'label': 'Max',        'field': 'max_score',  'align': 'left'},
                        {'name': 'difficulty', 'label': 'Difficulty', 'field': 'difficulty', 'align': 'left'},
                        {'name': 'time',       'label': 'Time',       'field': 'time',       'align': 'left'},
                    ]
                    rows_data = [
                        {
                            'rank':       i + 1,
                            'team':       row[0],
                            'score':      row[1],
                            'max_score':  row[2],
                            'difficulty': row[3].capitalize(),
                            'time':       row[4].astimezone(tz).strftime('%H:%M'),
                        }
                        for i, row in enumerate(rows)
                    ]
                    ui.table(columns=columns, rows=rows_data).classes('w-full').props('dark flat')

        date_picker.on('update:modelValue', lambda: asyncio.ensure_future(refresh()))
        with client_content:
            ui.timer(10.0, refresh)
        await refresh()

    show_login()


# Maps each goggle color to its image filename (green/blue have a double extension from upload)
GOGGLE_IMAGES = {
    'red':   '/resources/red_goggles.png',
    'green': '/resources/green_goggles.png.png',
    'blue':  '/resources/blue_goggles.png.png',
}


def _seen_through_goggle(hex_color: str, goggle: str) -> str:
    """Return the hex color as perceived through a single-channel goggle."""
    r = int(hex_color[1:3], 16)
    g = int(hex_color[3:5], 16)
    b = int(hex_color[5:7], 16)
    if goggle == 'red':
        return f'#{r:02x}0000'
    elif goggle == 'green':
        return f'#00{g:02x}00'
    else:
        return f'#0000{b:02x}'


@ui.page('/train')
def train():
    refs = {'preview': None, 'seen_boxes': []}

    with ui.column().classes('mx-auto mt-12 items-center gap-6 w-full max-w-3xl px-8'):
        ui.label('Color Trainer').classes('text-white text-2xl font-bold')

        ui.label(
            'Select a color below. The top box shows that color. '
            'The bottom row shows how the color appears through each pair of goggles.'
        ).classes('text-gray-300 text-sm text-center max-w-xl')

        ui.select(
            options={c: c.upper() for c in COLORS}, value='red', on_change=lambda e: update(e),
        ).props('dark outlined').classes('w-64 text-xl')

        # Large color preview box
        refs['preview'] = ui.element('div').style(
            f'background-color: {COLOR_HEX["red"]}; '
            'width: 100%; height: 100px; border-radius: 12px; '
            'display: flex; align-items: center; justify-content: center;'
        )
        with refs['preview']:
            refs['label'] = ui.label('RED').classes('text-4xl font-bold').style('color: black;')

        # Goggle simulator
        ui.label('Goggle Simulator').classes('text-white text-lg mt-4')

        with ui.row().classes('gap-8 mt-2 justify-center'):
            for goggle in ('red', 'green', 'blue'):
                with ui.column().classes('items-center gap-3'):
                    ui.image(GOGGLE_IMAGES[goggle]).classes('w-48')
                    seen_box = ui.element('div').style(
                        f'background-color: {_seen_through_goggle(COLOR_HEX["red"], goggle)}; '
                        'width: 192px; height: 80px; border-radius: 8px;'
                    )
                    refs['seen_boxes'].append(seen_box)

        def update(e):
            color = e.value
            hex_color = COLOR_HEX[color]
            refs['preview'].style(
                f'background-color: {hex_color}; '
                'width: 100%; height: 100px; border-radius: 12px; '
                'display: flex; align-items: center; justify-content: center;'
            )
            refs['label'].text = color.upper()
            for goggle, box in zip(('red', 'green', 'blue'), refs['seen_boxes']):
                box.style(
                    f'background-color: {_seen_through_goggle(hex_color, goggle)}; '
                    'width: 192px; height: 80px; border-radius: 8px;'
                )

        ui.button('Back', on_click=lambda: ui.navigate.to('/')).props('flat color=white').classes('mt-4')


ui.run(
    host='0.0.0.0',
    port=int(os.environ.get('PORT', 8080)),
    reload=False,
)
