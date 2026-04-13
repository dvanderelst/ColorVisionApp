from nicegui import ui
from library.utils import sample_colors
from library.trial import Trial


@ui.page('/')
def landing():
    with ui.column().classes('mx-auto mt-16 items-center gap-4'):
        ui.label('Color Vision Test').classes('text-3xl font-bold')
        ui.button('Start', on_click=lambda: ui.navigate.to('/trial')).classes('text-lg px-8 py-4')


@ui.page('/trial')
def trial():
    target = 'green'
    colors = sample_colors(9, target)
    Trial(target, colors, on_complete=lambda: ui.notify('Trial complete!'))


ui.run()
