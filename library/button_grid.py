from library.colors import colors as color_map
from components.button_grid import button_grid as _button_grid


def button_grid(color_names, cols=3, btn_width=150, btn_height=150,
                key="grid", sound_path="resources/click.wav"):
    """
    Render a grid of colored buttons from named colors.

    Parameters
    ----------
    color_names : list[str]
        List of named colors (e.g. 'red', 'green').
    cols : int
        Number of columns.
    btn_width, btn_height : int
        Button dimensions in pixels.
    key : str
        Streamlit component key.
    sound_path : str or None
        Path to click sound file.

    Returns
    -------
    int or None
        Index of the clicked button, or None.
    """
    hex_colors = [color_map[name] for name in color_names]
    return _button_grid(
        colors=hex_colors,
        cols=cols,
        btn_width=btn_width,
        btn_height=btn_height,
        key=key,
        sound_path=sound_path,
    )
