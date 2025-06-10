# fields/radio_button.py - CLEAN AND SIMPLE IMPLEMENTATION
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

        # Calculate field positioning
        field_x, field_width, field_y = self._get_field_position()
        starting_y = field_y
        
        # Draw label with adequate spacing
        if label:
            field_label_style = self.generator.label_styles['field_label']
            c.setFont(field_label_style.font_name, field_label_style.font_size)
            c.setFillColor(field_label_style.color)
            c.drawString(field_x, field_y, label)
            field_y -= 15  # Adequate space between label and options

        # Get options
        options_list = _get_options(options)
        if not options_list:
            options_list = [('yes', 'Yes'), ('no', 'No')]  # Default Yes/No

        # Draw radio buttons horizontally for simple cases
        if len(options_list) <= 3:
            self._draw_horizontal_radio_buttons(c, field_name, options_list, field_x, field_y)
            final_y = field_y - 20
        else:
            # Draw vertically for many options
            final_y = self._draw_vertical_radio_buttons(c, field_name, options_list, field_x, field_y)

        # Update positioning
        if self.generator.current_group is not None:
            self._handle_group_positioning(field_x, field_width, final_y, starting_y)
        else:
            self.generator.current_y = final_y - 8

        c.setFont(current_font, current_size)
        c.setFillColor(current_color)

    def _draw_horizontal_radio_buttons(self, c, field_name, options_list, field_x, field_y):
        """Draw radio buttons horizontally"""
        c.setFont("Helvetica", 9)
        c.setFillColor(self.colors['primary'])
        
        x_offset = 0
        for value, option_label in options_list:
            # Draw radio button
            c.acroForm.radio(
                name=field_name,
                tooltip=f"{field_name} - {option_label}",
                value=value,
                selected=0,
                x=field_x + x_offset,
                y=field_y - 8,
                size=10,
                borderColor=self.colors['border'],
                fillColor=self.colors['background'],
                textColor=self.colors['primary'],
                borderWidth=0.5
            )
            
            # Draw option label
            c.drawString(field_x + x_offset + 15, field_y - 5, option_label)
            
            # Move to next position
            option_width = 15 + c.stringWidth(option_label, "Helvetica", 9) + 20
            x_offset += option_width

    def _draw_vertical_radio_buttons(self, c, field_name, options_list, field_x, field_y):
        """Draw radio buttons vertically"""
        c.setFont("Helvetica", 9)
        c.setFillColor(self.colors['primary'])
        
        current_y = field_y
        for value, option_label in options_list:
            # Draw radio button
            c.acroForm.radio(
                name=field_name,
                tooltip=f"{field_name} - {option_label}",
                value=value,
                selected=0,
                x=field_x,
                y=current_y - 8,
                size=10,
                borderColor=self.colors['border'],
                fillColor=self.colors['background'],
                textColor=self.colors['primary'],
                borderWidth=0.5
            )
            
            # Draw option label
            c.drawString(field_x + 15, current_y - 5, option_label)
            current_y -= 18
        
        return current_y

    def _get_field_position(self):
        """Calculate position for field within group or regular flow"""
        field_x = self.margin_x
        field_width = self.field_width
        field_y = self.generator.current_y

        if self.generator.current_group is not None:
            group_index = len(self.generator.group_fields)
            column_index = group_index % self.generator.group_columns
            
            field_x = self.margin_x
            if column_index > 0:
                field_x += sum(self.generator.column_widths[:column_index])
                field_x += self.generator.group_spacing * column_index
            
            field_width = self.generator.column_widths[column_index]
            
            if column_index > 0 and self.generator.group_fields:
                row_index = group_index // self.generator.group_columns
                first_in_row_index = row_index * self.generator.group_columns
                if first_in_row_index < len(self.generator.group_fields):
                    first_field = self.generator.group_fields[first_in_row_index]
                    field_y = first_field.get('start_y', first_field.get('y', field_y))

        return field_x, field_width, field_y

    def _handle_group_positioning(self, field_x, field_width, final_y, start_y):
        """Handle positioning when field is in a group"""
        self.generator.group_fields.append({
            'name': 'radio_button',
            'x': field_x,
            'y': final_y,
            'start_y': start_y,
            'width': field_width
        })

        if len(self.generator.group_fields) % self.generator.group_columns == 0:
            row_start = len(self.generator.group_fields) - self.generator.group_columns
            row_fields = self.generator.group_fields[row_start:]
            min_y = min(f.get('y', self.generator.current_y) for f in row_fields)
            self.generator.current_y = min_y - 8