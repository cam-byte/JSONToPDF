# fields/radio_button.py - FIXED TO HANDLE REPORTLAB RADIO GROUP REQUIREMENTS
from utils import _get_options, _check_page_break, draw_wrapped_text, calculate_wrapped_text_height

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
        
        # Draw label with text wrapping using actual field width
        if label:
            field_label_style = self.generator.label_styles['field_label']
            max_label_width = field_width * 0.88  # Use actual field width
            
            final_label_y = draw_wrapped_text(
                c, label, field_x, field_y, max_label_width,
                field_label_style.font_name, field_label_style.font_size,
                field_label_style.color
            )
            
            field_y = final_label_y + 2

        # Get options
        options_list = _get_options(options)
        if not options_list:
            options_list = [('yes', 'Yes'), ('no', 'No')]  # Default Yes/No

        # CRITICAL FIX: Ensure we have at least 2 options for ReportLab
        if len(options_list) < 2:
            # If only one option, add a "Not Selected" option
            options_list.append(('not_selected', 'Not Selected'))

        # Draw radio buttons
        self._draw_horizontal_radio_buttons(c, field_name, options_list, field_x, field_y, field_width)
        final_y = field_y - 25

        if self.generator.current_group is not None:
            self._handle_group_positioning(field_x, field_width, final_y, starting_y)
        else:
            self.generator.current_y = final_y - 8

        c.setFont(current_font, current_size)
        c.setFillColor(current_color)

    def _can_fit_horizontally(self, c, options_list, field_width):
        """Check if radio buttons can fit horizontally in the available width"""
        c.setFont("Helvetica", 9)
        total_width = 0
        for value, option_label in options_list:
            option_width = 15 + c.stringWidth(option_label, "Helvetica", 9) + 20
            total_width += option_width
        
        return total_width <= (field_width * 0.9)

    def _draw_horizontal_radio_buttons(self, c, field_name, options_list, field_x, field_y, field_width):
        """Draw radio buttons horizontally"""
        c.setFont("Helvetica", 9)
        c.setFillColor(self.colors['primary'])
        
        x_offset = 0
        max_width = field_width * 0.9  # Use 90% of available width
        
        for value, option_label in options_list:
            # Check if we have space for this option
            option_width = 3 + c.stringWidth(option_label, "Helvetica", 9) + 20
            if x_offset + option_width > max_width and x_offset > 0:
                break  # Stop if we'd exceed available width
            
            try:
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
                c.drawString(field_x + x_offset + 15, field_y - 6, option_label)
                x_offset += option_width
                
            except Exception as e:
                print(f"Error creating radio button {field_name}:{value} - {e}")
                # Fallback: create as text field if radio fails
                c.acroForm.textfield(
                    name=f"{field_name}_{value}",
                    tooltip=f"{field_name} - {option_label}",
                    x=field_x + x_offset,
                    y=field_y - 18,
                    width=option_width - 20,
                    height=15,
                    fontSize=9,
                    borderWidth=0.5,
                    borderColor=self.colors['border'],
                    fillColor=self.colors['background'],
                    textColor=self.colors['primary'],
                    fieldFlags=0
                )
                x_offset += option_width

    def _draw_vertical_radio_buttons(self, c, field_name, options_list, field_x, field_y, field_width):
        """Draw radio buttons vertically"""
        c.setFont("Helvetica", 9)
        c.setFillColor(self.colors['primary'])
        
        current_y = field_y
        max_label_width = field_width * 0.9 - 20  # Leave space for radio button
        
        for value, option_label in options_list:
            try:
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
                
                # Draw wrapped option label
                final_option_y = draw_wrapped_text(
                    c, option_label, field_x + 15, current_y - 5, max_label_width,
                    "Helvetica", 9, self.colors['primary']
                )
                
                current_y = final_option_y - 1  # Space between options
                
            except Exception as e:
                print(f"Error creating radio button {field_name}:{value} - {e}")
                # Fallback: create as text field if radio fails
                c.acroForm.textfield(
                    name=f"{field_name}_{value}",
                    tooltip=f"{field_name} - {option_label}",
                    x=field_x,
                    y=current_y - 18,
                    width=field_width * 0.8,
                    height=15,
                    fontSize=9,
                    borderWidth=0.5,
                    borderColor=self.colors['border'],
                    fillColor=self.colors['background'],
                    textColor=self.colors['primary'],
                    fieldFlags=0
                )
                current_y -= 25
        
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