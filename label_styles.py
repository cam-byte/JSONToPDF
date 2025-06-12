# label_styles.py - CLEAN READABLE SPACING
from reportlab.lib import colors

class LabelStyle:
    """Simple class to hold label styling information"""
    def __init__(self, font_name, font_size, color, spacing_before=0, spacing_after=0, alignment='left'):
        self.font_name = font_name
        self.font_size = font_size
        self.color = color
        self.spacing_before = spacing_before
        self.spacing_after = spacing_after
        self.alignment = alignment

# Clean, readable spacing that prevents overlapping
LABEL_STYLES = {
    'h1': LabelStyle(
        font_name='Helvetica-Bold',
        font_size=16,
        color=colors.black,
        spacing_before=8,      # Space before h1 headers
        spacing_after=12,      # Reasonable spacing
        alignment='center'
    ),
    'h3': LabelStyle(
        font_name='Helvetica-Bold',
        font_size=12,
        color=colors.black,
        spacing_before=10,     # Space before h3 headers
        spacing_after=8,       # Reasonable spacing
        alignment='left'
    ),
    'h4': LabelStyle(
        font_name='Helvetica-Bold',
        font_size=10,
        color=colors.black,
        spacing_before=8,      # Space before h4 headers
        spacing_after=6,       # Reasonable spacing
        alignment='left'
    ),
    'h5': LabelStyle(
        font_name='Helvetica',
        font_size=9,
        color=colors.Color(0.4, 0.4, 0.4),
        spacing_before=6,      # Space before h5 headers
        spacing_after=4,       # Reasonable spacing
        alignment='left'
    ),
    'p': LabelStyle(
        font_name='Helvetica',
        font_size=10,
        color=colors.black,
        spacing_before=21,      # Space before paragraphs
        spacing_after=21,      # Reasonable spacing
        alignment='left'
    ),
    'regular': LabelStyle(
        font_name='Helvetica',
        font_size=10,
        color=colors.black,
        spacing_before=2,      # Minimal space before regular text
        spacing_after=4,       # Reasonable spacing
        alignment='left'
    ),
    'field_label': LabelStyle(
        font_name='Helvetica',
        font_size=9,
        color=colors.Color(0.3, 0.3, 0.3),
        spacing_before=4,      # Space before field labels
        spacing_after=3,       # Adequate spacing for field labels
        alignment='left'
    )
}