# label_styles.py - CLEAN READABLE SPACING
from reportlab.lib import colors
from utils import LabelStyle

# Clean, readable spacing that prevents overlapping
LABEL_STYLES = {
    'h1': LabelStyle(
        font_name='Helvetica-Bold',
        font_size=14,
        color=colors.black,
        spacing_after=12,      # Reasonable spacing
        alignment='left'
    ),
    'h3': LabelStyle(
        font_name='Helvetica-Bold',
        font_size=12,
        color=colors.black,
        spacing_after=8,       # Reasonable spacing
        alignment='left'
    ),
    'h4': LabelStyle(
        font_name='Helvetica-Bold',
        font_size=10,
        color=colors.black,
        spacing_after=6,       # Reasonable spacing
        alignment='left'
    ),
    'h5': LabelStyle(
        font_name='Helvetica',
        font_size=9,
        color=colors.Color(0.4, 0.4, 0.4),
        spacing_after=4,       # Reasonable spacing
        alignment='left'
    ),
    'p': LabelStyle(
        font_name='Helvetica',
        font_size=10,
        color=colors.black,
        spacing_after=6,       # Reasonable spacing
        alignment='left'
    ),
    'regular': LabelStyle(
        font_name='Helvetica',
        font_size=10,
        color=colors.black,
        spacing_after=4,       # Reasonable spacing
        alignment='left'
    ),
    'field_label': LabelStyle(
        font_name='Helvetica',
        font_size=9,
        color=colors.Color(0.3, 0.3, 0.3),
        spacing_after=3,       # Adequate spacing for field labels
        alignment='left'
    )
}