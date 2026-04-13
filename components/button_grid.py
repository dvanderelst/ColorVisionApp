import base64
import os
import streamlit.components.v1 as components

_component_func = components.declare_component(
    "button_grid",
    path=os.path.join(os.path.dirname(__file__), "button_grid"),
)


def button_grid(colors, cols=3, btn_width=150, btn_height=150, key=None, sound_path=None):
    """
    Render a grid of colored buttons.

    Parameters
    ----------
    colors : list[str]
        List of hex color strings, one per button.
    cols : int
        Number of columns in the grid.
    btn_width : int
        Width of each button in pixels.
    btn_height : int
        Height of each button in pixels.
    key : str, optional
        Streamlit component key.
    sound_path : str, optional
        Path to an audio file to play on click.

    Returns
    -------
    int or None
        Index of the clicked button, or None if nothing was clicked.
    """
    sound_b64 = None
    sound_ext = None

    if sound_path is not None:
        with open(sound_path, "rb") as f:
            sound_b64 = base64.b64encode(f.read()).decode("utf-8")
        sound_ext = os.path.splitext(sound_path)[1].lstrip(".")

    value = _component_func(
        colors=colors,
        cols=cols,
        btn_width=btn_width,
        btn_height=btn_height,
        sound_b64=sound_b64,
        sound_ext=sound_ext,
        key=key,
        default=None,
    )

    return value
