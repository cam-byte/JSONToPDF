# fields/check_box.py - WITH TEXT WRAPPING
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
        # Draw label with text wrapping
        if label:
            field_label_style = self.generator.label_styles['field_label']
            max_label_width = field_width * 0.9
            
            final_label_y = draw_wrapped_text(
                c, label, field_x, field_y, max_label_width,
                field_label_style.font_name, field_label_style.font_size,
                field_label_style.color
            )
            
            field_y = final_label_y - 15

        field_y_position = field_y - 3

        c.acroForm.checkbox(
            name=field_name,
            tooltip=label,
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
        # Draw main label with text wrapping
        if label:
            field_label_style = self.generator.label_styles['field_label']
            max_label_width = field_width * 0.9
            
            final_label_y = draw_wrapped_text(
                c, label, field_x, field_y, max_label_width,
                field_label_style.font_name, field_label_style.font_size,
                field_label_style.color
            )
            
            field_y = final_label_y - 15

        current_y = field_y
        c.setFont("Helvetica", 9)
        c.setFillColor(self.colors['primary'])
        max_option_width = field_width * 0.9 - 20  # Leave space for checkbox
        
        for i, (value, option_label) in enumerate(options_list):
            clean_option_label = _strip_html_tags(option_label)
            
            checkbox_name = f"{field_name}_{value}"
            c.acroForm.checkbox(
                name=checkbox_name,
                tooltip=f"{label} - {clean_option_label}",
                x=field_x,
                y=current_y - 8,
                size=12,
                borderColor=self.colors['border'],
                fillColor=self.colors['background'],
                textColor=self.colors['primary'],
                borderWidth=0.5,
                checked=False
            )
            
            # Draw wrapped option label
            final_option_y = draw_wrapped_text(
                c, clean_option_label, field_x + 18, current_y - 5, max_option_width,
                "Helvetica", 9, self.colors['primary']
            )
            
            current_y = final_option_y - 8  # Space between options

        final_field_y = current_y

        if self.generator.current_group is not None:
            self._handle_group_positioning(field_x, field_width, final_field_y, starting_y)
        else:
            self.generator.current_y = final_field_y - 8

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