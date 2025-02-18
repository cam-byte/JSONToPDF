# fields/radio_button.py
from utils import _get_options, _check_page_break

class RadioButton:
    def __init__(self, generator, canvas):
        self.generator = generator
        self.canvas = canvas
        self.colors = generator.colors
        self.margin_x = generator.margin_x
        self.current_y = generator.current_y

    def draw(self, field_name, label, options):
        c = self.canvas
        current_font = c._fontname
        current_size = c._fontsize
        current_color = c._fillColorObj

        options_list = _get_options(options)
        radio_size = 7
        
        c.setFont("Helvetica", 9)
        c.setFillColor(self.colors['primary'])

        num_options = len(options_list)
        total_width = (num_options * radio_size) + ((num_options - 1) * 30) + (num_options * c.stringWidth("  ", "Helvetica", 9))  
        x_start = self.margin_x
        x_offset = 0

        for value, label in options_list:
            if _check_page_break(self.generator, c, 20):
                x_offset = 0
                x_start = self.margin_x
                continue

            c.acroForm.radio(
                name=field_name,
                value=value,
                selected=False,
                x=x_start + x_offset,
                y=self.generator.current_y - radio_size,
                size=radio_size,
                buttonStyle='circle',
                borderStyle='solid',
                borderWidth=0.5,
                borderColor=self.colors['border'],
                fillColor=self.colors['background'],
                textColor=self.colors['primary'],
                forceBorder=True,
                fieldFlags=0
            )

            label_width = c.stringWidth(label, "Helvetica", 9)
            c.drawString(x_start + x_offset + 10, self.generator.current_y - 6, label)
            x_offset += radio_size + 15 + label_width  

        self.generator.current_y -= 30

        c.setFont(current_font, current_size)
        c.setFillColor(current_color)