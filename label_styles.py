# label_styles.py
from dataclasses import dataclass
from reportlab.lib import colors
from constants import COLORS

@dataclass
class LabelStyle:
    font_name: str
    font_size: int
    color: colors.Color
    spacing_after: int
    alignment: str = 'left'

LABEL_STYLES = {
    'field_label': LabelStyle(
        font_name="Helvetica-Bold",
        font_size=8,
        color=COLORS['secondary'],
        spacing_after=8
    ),
    'h1': LabelStyle(
        font_name="Helvetica-Bold",
        font_size=18,
        color=COLORS['accent'],
        spacing_after=35,
        alignment='center'
    ),
    'h3': LabelStyle(
        font_name="Helvetica-Bold",
        font_size=14,
        color=COLORS['accent'],
        spacing_after=25
    ),
    'h4': LabelStyle(
        font_name="Helvetica-Oblique",
        font_size=6,
        color=COLORS['secondary'],
        spacing_after=20
    ),
    'p': LabelStyle(
        font_name="Helvetica",
        font_size=10,
        color=COLORS['secondary'],
        spacing_after=30
    ),
    'regular': LabelStyle(
        font_name="Helvetica",
        font_size=9,
        color=COLORS['secondary'],
        spacing_after=12
    )
}