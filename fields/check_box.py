# fields/check_box.py
from utils import _get_options, _check_page_break, _strip_html_tags, _wrap_text

class CheckBox:
    def __init__(self, generator, canvas):
        self.generator = generator
        self.canvas = canvas
        self.colors = generator.colors
        self.margin_x = generator.margin_x
        self.field_width = generator.field_width

    def draw(self, field_name, label, options):
        c = self.canvas
        current_font = c._fontname
        current_size = c._fontsize
        current_color = c._fillColorObj

        options_list = _get_options(options)
        checkbox_size = 7

        c.setFont("Helvetica", 9)
        c.setFillColor(self.colors['primary'])

        for value, label in options_list:
            if _check_page_break(self.generator, c, 20):
                continue

            cleaned_label = _strip_html_tags(label)
            wrapped_lines = _wrap_text(cleaned_label, self.field_width - 20)

            c.acroForm.checkbox(
                name=f"{field_name}_{value}",
                checked=False,
                x=self.margin_x,
                y=self.generator.current_y - checkbox_size,
                size=checkbox_size,
                buttonStyle='check',
                borderStyle='solid',
                borderWidth=0.5,
                borderColor=self.colors['border'],
                fillColor=self.colors['background'],
                textColor=self.colors['primary'],
                forceBorder=True,
                fieldFlags=0
            )
            
            current_line_y = self.generator.current_y
            for line in wrapped_lines:
                c.drawString(self.margin_x + 15, current_line_y - 6, line)
                current_line_y -= 15
            
            self.generator.current_y -= (len(wrapped_lines) * 15 + 10)

        c.setFont(current_font, current_size)
        c.setFillColor(current_color)