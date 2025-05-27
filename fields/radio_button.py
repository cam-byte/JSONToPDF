# fields/radio_button.py
from utils import _get_options, _check_page_break

class RadioButton:
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

        # Calculate field positioning (similar to TextField)
        field_x = self.margin_x
        field_width = self.field_width
        
        if self.generator.current_group is not None:
            group_index = len(self.generator.group_fields)
            column_index = group_index % self.generator.group_columns
            
            # Calculate x position
            field_x = self.margin_x
            if column_index > 0:
                # Add widths of previous columns plus spacing
                field_x += sum(self.generator.column_widths[:column_index])
                field_x += self.generator.group_spacing * column_index
            
            field_width = self.generator.column_widths[column_index]
            
            # If not first in row, align with previous field's y position
            if column_index > 0:
                previous_field = self.generator.group_fields[group_index - 1]
                self.generator.current_y = previous_field['y']

        options_list = _get_options(options)
        radio_size = 7
        
        c.setFont("Helvetica", 8)
        c.setFillColor(self.colors['primary'])

        x_offset = 0

        for value, option_label in options_list:
            if _check_page_break(self.generator, c, 20):
                x_offset = 0
                continue

            # Make sure radio button fits within the field width
            if x_offset + radio_size + 50 > field_width:  # 50px buffer for label
                break

            c.acroForm.radio(
                name=field_name,
                value=value,
                selected=False,
                x=field_x + x_offset,
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

            label_width = c.stringWidth(option_label, "Helvetica", 8)
            c.drawString(field_x + x_offset + 10, self.generator.current_y - 6, option_label)
            x_offset += radio_size + 15 + label_width

        # Store field info for group positioning
        if self.generator.current_group is not None:
            self.generator.group_fields.append({
                'name': field_name,
                'x': field_x,
                'y': self.generator.current_y,
                'width': field_width
            })

        # Move to next line only if last in row or not in a group
        if (not self.generator.current_group or 
            (len(self.generator.group_fields) % self.generator.group_columns == 0)):
            self.generator.current_y -= 30

        c.setFont(current_font, current_size)
        c.setFillColor(current_color)