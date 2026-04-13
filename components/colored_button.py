import base64
import os
import streamlit.components.v1 as components

_component_func = components.declare_component(
    "colored_button",
    path=os.path.join(os.path.dirname(__file__), "colored_button"),
)


def colored_button(
    label,
    bg_color,
    text_color="#fff",
    width=150,
    height=50,
    key=None,
    sound_path=None,
):
    sound_b64 = None
    sound_ext = None

    if sound_path is not None:
        with open(sound_path, "rb") as f:
            sound_b64 = base64.b64encode(f.read()).decode("utf-8")
        sound_ext = os.path.splitext(sound_path)[1].lstrip(".")

    value = _component_func(
        label=label,
        bg_color=bg_color,
        text_color=text_color,
        width=width,
        height=height,
        sound_b64=sound_b64,
        sound_ext=sound_ext,
        key=key,
        default=False,
    )

    return bool(value)
