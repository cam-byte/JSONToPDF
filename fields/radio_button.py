# fields/radio_button.py - FIXED: Clean radio buttons with proper capitalization
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
            max_label_width = field_width * 0.88
            
            final_label_y = draw_wrapped_text(
                c, label, field_x, field_y, max_label_width,
                field_label_style.font_name, field_label_style.font_size,
                field_label_style.color
            )
            
            field_y = final_label_y + 7  # Better spacing after label

        # Get options and ensure proper capitalization
        options_list = _get_options(options)
        if not options_list:
            options_list = [('Yes', 'Yes'), ('No', 'No')]  # Default Yes/No with proper caps

        # Capitalize all option values and labels
        options_list = [(value.capitalize() if isinstance(value, str) else value, 
                        label.capitalize() if isinstance(label, str) else label) 
                       for value, label in options_list]

        # Ensure we have at least 2 options for ReportLab radio groups
        if len(options_list) < 2:
            options_list.append(('Not_Selected', 'Not Selected'))

        # Draw radio buttons
        final_y = self._draw_radio_buttons_clean(c, field_name, options_list, field_x, field_y, field_width)

        if self.generator.current_group is not None:
            self._handle_group_positioning(field_x, field_width, final_y, starting_y)
        else:
            self.generator.current_y = final_y - 8

        c.setFont(current_font, current_size)
        c.setFillColor(current_color)

    def _draw_radio_buttons_clean(self, c, field_name, options_list, field_x, field_y, field_width):
        """Draw radio buttons with clean positioning - ALWAYS HORIZONTAL"""
        c.setFont("Helvetica", 9)
        c.setFillColor(self.colors['primary'])
        
        # ALWAYS use horizontal layout - no vertical option
        return self._draw_horizontal_radio_buttons(c, field_name, options_list, field_x, field_y, field_width)

    def _draw_horizontal_radio_buttons(self, c, field_name, options_list, field_x, field_y, field_width):
        """Draw radio buttons horizontally - ACTUALLY HORIZONTAL, not wrapping every option"""
        x_offset = 0
        max_width = field_width * 0.95  # Use more of the available width
        current_row_y = field_y
        
        for i, (value, option_label) in enumerate(options_list):
            option_text_width = c.stringWidth(option_label, "Helvetica", 9)
            option_width = 18 + option_text_width + 8  # Reduced spacing between options
            
            # Only wrap if this option truly won't fit AND we're not the first option on the row
            if x_offset > 0 and x_offset + option_width > max_width:
                current_row_y -= 25  # Move to next row
                x_offset = 0
            
            radio_x = field_x + x_offset
            radio_y = current_row_y - 15
            text_x = radio_x + 18
            text_y = current_row_y - 12
            
            # Create radio button
            c.acroForm.radio(
                name=field_name,  # SAME NAME for all buttons in group!
                tooltip=f"{field_name}: {option_label}",
                value=value,
                selected=0,
                x=radio_x,
                y=radio_y,
                size=12,
                borderColor=self.colors.get('border', 'black'),
                fillColor=self.colors.get('background', 'white'),
                textColor=self.colors.get('primary', 'black'),
                borderWidth=1,
                forceBorder=True,
                fieldFlags=49152,
                annotationFlags=4
            )
            
            # Draw option label
            c.setFillColor(self.colors.get('primary', 'black'))
            c.drawString(text_x, text_y, option_label)
            x_offset += option_width
        
        return current_row_y - 20

    def _can_fit_horizontally(self, c, options_list, field_width):
        """Check horizontal spacing - kept for potential future use"""
        c.setFont("Helvetica", 9)
        total_width = 0
        for value, option_label in options_list:
            option_width = 18 + c.stringWidth(option_label, "Helvetica", 9) + 25
            total_width += option_width
        
        return total_width <= (field_width * 0.9)

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