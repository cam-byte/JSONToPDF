# label_manager.py - COMPACT VERSION FOR BETTER SPACE USAGE
import re
from utils import _strip_html_tags, _wrap_text

class LabelManager:
    def __init__(self, generator):
        self.generator = generator
        self.label_styles = generator.label_styles
        self.margin_x = generator.margin_x
        self.field_width = generator.field_width
        self.colors = generator.colors

    def get_label_style(self, field_type, label):
        """Determine the appropriate label style based on content"""
        if field_type == 'label':
            if '<h1>' in label.lower():
                return self.label_styles['h1']
            elif '<h3>' in label.lower():
                return self.label_styles['h3']
            elif '<h4>' in label.lower():
                return self.label_styles['h4']
            elif '<h5>' in label.lower():
                return self.label_styles['h5']
            elif '<p>' in label.lower():
                return self.label_styles['p']
            else:
                return self.label_styles['regular']
        else:
            return self.label_styles['field_label']

    def draw_label(self, canvas, label, style, draw_line=False, spacing_before=None):
        current_font = canvas._fontname
        current_size = canvas._fontsize
        current_color = canvas._fillColorObj

        # Clean the label text
        clean_text = _strip_html_tags(label)

        # Skip empty labels
        if not clean_text.strip():
            return

        # Apply spacing_before if provided, otherwise use style's spacing_before
        if spacing_before is not None:
            self.generator.current_y -= spacing_before
        elif hasattr(style, 'spacing_before'):
            self.generator.current_y -= style.spacing_before

        # Set font and color
        canvas.setFont(style.font_name, style.font_size)
        canvas.setFillColor(style.color)

        # Determine if this is a paragraph
        is_paragraph = "<p>" in label.lower() and "</p>" in label.lower()

        # Use full page width for paragraphs, field width for others
        if is_paragraph:
            wrap_width = self.generator.page_width - 2 * self.generator.margin_x
            line_height = style.font_size + 6  # Increased line height for paragraphs
        else:
            wrap_width = self.field_width
            line_height = style.font_size + 1  # Normal line height for other labels

        wrapped_lines = _wrap_text(clean_text, wrap_width, style.font_size, style.font_name)

        # Handle paragraph margins if applicable
        if is_paragraph and hasattr(style, 'paragraph_margin_top'):
            self.generator.current_y -= style.paragraph_margin_top

        # Draw each line
        current_line_y = self.generator.current_y
        lines_drawn = 0

        for line in wrapped_lines:
            if line.strip():
                canvas.drawString(self.margin_x, current_line_y, line)
                current_line_y -= line_height
                lines_drawn += 1

        # Minimal spacing after labels
        if lines_drawn > 0:
            actual_text_height = lines_drawn * line_height
            self.generator.current_y = self.generator.current_y - actual_text_height - style.spacing_after
        else:
            # Even for empty content, minimal movement
            self.generator.current_y -= style.spacing_after

        if is_paragraph and hasattr(style, 'paragraph_margin_bottom'):
            self.generator.current_y -= style.paragraph_margin_bottom

        # Draw underline for h1 headers if requested
        if draw_line and lines_drawn > 0:
            line_y = current_line_y + line_height + -5
            canvas.setStrokeColor(self.colors['accent'])
            canvas.setLineWidth(1)  # Thinner line
            canvas.line(self.margin_x, line_y, self.margin_x + wrap_width, line_y)

        # Restore original settings
        canvas.setFont(current_font, current_size)
        canvas.setFillColor(current_color)
