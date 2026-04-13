import streamlit as st
from library.utils import sample_colors
from library.button_grid import button_grid

st.title("colored_button demo")

target_color = 'green'

st.header(target_color.capitalize())
button_colors = sample_colors(9, 'green')
clicked = button_grid(button_colors, cols=3)


