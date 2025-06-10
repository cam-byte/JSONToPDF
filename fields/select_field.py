# fields/select_field.py - FIXED VERSION TO AVOID REPORTLAB BUG
from utils import _get_options, _check_page_break

class SelectField:
    def __init__(self, generator, canvas):
        self.generator = generator
        self.canvas = canvas
        self.colors = generator.colors
        self.margin_x = generator.margin_x
        self.field_width = generator.field_width
        self.field_height = generator.field_height

    def draw(self, field_name, label, options):
        c = self.canvas
        current_font = c._fontname
        current_size = c._fontsize
        current_color = c._fillColorObj

        # Calculate field positioning
        field_x, field_width, field_y = self._get_field_position()
        starting_y = field_y
        
        # Draw label with consistent spacing
        label_height = 0
        if label:
            field_label_style = self.generator.label_styles['field_label']
            c.setFont(field_label_style.font_name, field_label_style.font_size)
            c.setFillColor(field_label_style.color)
            c.drawString(field_x, field_y + 3, label)
            label_height = field_label_style.font_size + 3
            field_y -= 15

        # Set minimum field width to prevent ReportLab issues
        min_width = 100
        field_width = max(field_width, min_width)

        # Position field below label
        field_y_position = field_y - 5

        # WORKAROUND: Use textfield instead of choice to avoid ReportLab bug
        # We'll add the options as a comment or tooltip
        options_list = _get_options(options)
        if options_list:
            # Create a tooltip with all options
            option_strings = [f"{value}: {option_label}" for value, option_label in options_list]
            tooltip_text = f"{label} - Options: {', '.join([ol for v, ol in options_list])}"
        else:
            tooltip_text = label

        # Draw as a regular text field with options in tooltip
        c.acroForm.textfield(
            name=field_name,
            tooltip=tooltip_text,
            x=field_x,
            y=field_y_position - self.field_height,
            width=field_width,
            height=self.field_height,
            fontSize=10,
            borderWidth=0.5,
            borderColor=self.colors['border'],
            fillColor=self.colors['background'],
            textColor=self.colors['primary'],
            fieldFlags=0
        )

        # Optionally, draw the options next to the field for reference
        if options_list and len(options_list) <= 3:  # Only for short option lists
            c.setFont("Helvetica", 8)
            c.setFillColor(self.colors['secondary'])
            options_text = " / ".join([ol for v, ol in options_list])
            c.drawString(field_x + field_width + 10, field_y_position - 8, f"({options_text})")

        final_field_y = field_y_position - self.field_height

        # Update positioning for group or regular flow
        if self.generator.current_group is not None:
            self._handle_group_positioning(field_x, field_width, final_field_y, starting_y)
        else:
            self.generator.current_y = final_field_y - 10

        c.setFont(current_font, current_size)
        c.setFillColor(current_color)

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
            'name': 'select_field',
            'x': field_x,
            'y': final_y,
            'start_y': start_y,
            'width': field_width
        })

        if len(self.generator.group_fields) % self.generator.group_columns == 0:
            row_start = len(self.generator.group_fields) - self.generator.group_columns
            row_fields = self.generator.group_fields[row_start:]
            min_y = min(f.get('y', self.generator.current_y) for f in row_fields)
            self.generator.current_y = min_y - 10
