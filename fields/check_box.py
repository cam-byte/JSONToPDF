# fields/check_box.py - SIMPLIFIED VERSION THAT HANDLES PARAGRAPH WRAPPING
from utils import _get_options, _check_page_break, _strip_html_tags, draw_wrapped_text, calculate_wrapped_text_height

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

        # Store options for access in other methods
        self.current_options = options

        # Calculate field positioning
        field_x, field_width, field_y = self._get_field_position()
        starting_y = field_y
        
        # Get checkbox options
        options_list = _get_options(options)
        
        if not options_list:
            self._draw_single_checkbox(c, field_name, label, field_x, field_width, field_y, starting_y)
        else:
            self._draw_multiple_checkboxes(c, field_name, label, options_list, field_x, field_width, field_y, starting_y)

        c.setFont(current_font, current_size)
        c.setFillColor(current_color)

    def _draw_single_checkbox(self, c, field_name, label, field_x, field_width, field_y, starting_y):
        # Check if this is a paragraph label (could be in label or in options)
        is_paragraph_label = label and "<p>" in label.lower() and "</p>" in label.lower()
        
        # For single checkboxes, check if the checkbox text is in the options
        options_list = _get_options(self.current_options if hasattr(self, 'current_options') else {})
        checkbox_text = label
        is_paragraph = is_paragraph_label
        
        # If no label but we have options, use the first option value as the checkbox text
        if not label and options_list:
            checkbox_text = options_list[0][1]  # Get the value from (key, value) tuple
            is_paragraph = "<p>" in checkbox_text.lower() and "</p>" in checkbox_text.lower()
            print(f"DEBUG: Using option text for {field_name}: {checkbox_text[:50]}...")
        
        # Draw label with text wrapping
        if checkbox_text and checkbox_text.strip():
            style = self.generator.label_manager.get_label_style('checkbox', checkbox_text)
            
            # Save current position
            self.generator.current_y = field_y
            
            if is_paragraph:
                # For paragraph labels, don't pass field_width so it uses full page width
                print(f"DEBUG: Drawing paragraph checkbox for {field_name}")
                self.generator.label_manager.draw_label(c, checkbox_text, style)
            else:
                # For regular checkbox labels, constrain to field width
                print(f"DEBUG: Drawing regular checkbox for {field_name} with width {field_width}")
                self.generator.label_manager.draw_label(c, checkbox_text, style, field_width=field_width * 0.9)
            
            # Calculate the actual space used by the label
            field_y = self.generator.current_y - 5

        field_y_position = field_y - 3

        c.acroForm.checkbox(
            name=field_name,
            tooltip=_strip_html_tags(checkbox_text) if checkbox_text else field_name,
            x=field_x,
            y=field_y_position - 12,
            size=12,
            borderColor=self.colors['border'],
            fillColor=self.colors['background'],
            textColor=self.colors['primary'],
            borderWidth=0.5,
            checked=False
        )

        final_field_y = field_y_position - 12

        if self.generator.current_group is not None:
            self._handle_group_positioning(field_x, field_width, final_field_y, starting_y)
        else:
            self.generator.current_y = final_field_y - 8

    def _draw_multiple_checkboxes(self, c, field_name, label, options_list, field_x, field_width, field_y, starting_y):
        # Check if this is a paragraph label
        is_paragraph = label and "<p>" in label.lower() and "</p>" in label.lower()
        
        # Draw main label with text wrapping
        if label:
            style = self.generator.label_manager.get_label_style('checkbox', label)
            
            # Save current position
            self.generator.current_y = field_y
            
            if is_paragraph:
                # For paragraph labels, don't pass field_width so it uses full page width
                print(f"DEBUG: Drawing paragraph checkbox label for {field_name}")
                self.generator.label_manager.draw_label(c, label, style)
            else:
                # For regular checkbox labels, constrain to field width
                print(f"DEBUG: Drawing regular checkbox label for {field_name} with width {field_width}")
                self.generator.label_manager.draw_label(c, label, style, field_width=field_width * 0.9)
            
            # Calculate the actual space used by the label
            field_y = self.generator.current_y - 5

        current_y = field_y
        c.setFont("Helvetica", 9)
        c.setFillColor(self.colors['primary'])

        # Layout settings
        checkbox_size = 12
        padding = 6  # space between checkbox and label
        option_spacing = 30  # space between options
        row_spacing = 18     # vertical space between rows
        max_label_width = 80 # max width for each label (adjust as needed)

        available_width = field_width
        start_x = field_x
        current_x = start_x

        from reportlab.pdfbase.pdfmetrics import stringWidth

        # Track the max height of the current row
        row_max_height = checkbox_size

        for i, (value, option_label) in enumerate(options_list):
            clean_option_label = _strip_html_tags(option_label)
            label_width = min(stringWidth(clean_option_label, "Helvetica", 9), max_label_width)
            total_width = checkbox_size + padding + label_width + option_spacing

            # If this checkbox would overflow, wrap to next row
            if current_x + total_width > start_x + available_width:
                current_x = start_x
                current_y -= (row_max_height + row_spacing)
                row_max_height = checkbox_size  # reset for new row

            checkbox_name = f"{field_name}_{value}"
            c.acroForm.checkbox(
                name=checkbox_name,
                tooltip=f"{_strip_html_tags(label) if label else field_name} - {clean_option_label}",
                x=current_x,
                y=current_y - checkbox_size + 2,
                size=checkbox_size,
                borderColor=self.colors['border'],
                fillColor=self.colors['background'],
                textColor=self.colors['primary'],
                borderWidth=0.5,
                checked=False
            )

            # Draw label to the right of the checkbox
            label_x = current_x + checkbox_size + padding
            label_y = current_y
            c.drawString(label_x, label_y, clean_option_label)

            # Update for next checkbox
            current_x += total_width

        final_field_y = current_y - row_max_height

        if self.generator.current_group is not None:
            self._handle_group_positioning(field_x, field_width, final_field_y, starting_y)
        else:
            self.generator.current_y = final_field_y - 8  # Add some space below the row

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
            'name': 'checkbox',
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