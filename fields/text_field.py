# fields/text_field.py - FIXED WITH PROPER GROUP WIDTH HANDLING
from utils import _check_page_break, draw_wrapped_text, calculate_wrapped_text_height, debug_group_positioning, get_effective_field_width

class TextField:
    def __init__(self, generator, canvas):
        self.generator = generator
        self.canvas = canvas
        self.colors = generator.colors
        self.margin_x = generator.margin_x
        self.field_width = generator.field_width
        self.field_height = generator.field_height

    def draw(self, field_name, label):
        c = self.canvas
        current_font = c._fontname
        current_size = c._fontsize
        current_color = c._fillColorObj

        # DEBUG: Print positioning info
        debug_group_positioning(self.generator, field_name, label or "")

        # Calculate field positioning
        field_x, field_width, field_y = self._get_field_position()
        starting_y = field_y
        
        # Draw label with text wrapping using ACTUAL field width
        if label:
            field_label_style = self.generator.label_styles['field_label']
            
            # CRITICAL FIX: Use actual field width, not page width
            max_label_width = field_width * 0.88  # Use 88% of the actual column width
            
            print(f"DEBUG TextField: Field width = {field_width}, Max label width = {max_label_width}")
            
            # Calculate height needed for wrapped text
            label_height = calculate_wrapped_text_height(
                c, label, max_label_width, 
                field_label_style.font_name, field_label_style.font_size
            )
            
            # Draw wrapped label
            final_label_y = draw_wrapped_text(
                c, label, field_x, field_y, max_label_width,
                field_label_style.font_name, field_label_style.font_size,
                field_label_style.color
            )
            
            # Update field_y based on actual label height
            field_y = final_label_y - 5  # Space between label and field

        # Position field below label
        field_y_position = field_y

        # Draw text field
        c.acroForm.textfield(
            name=field_name,
            tooltip=label,
            x=field_x,
            y=field_y_position - self.field_height,
            width=field_width,  # Use actual field width
            height=self.field_height,
            fontSize=10,
            borderWidth=0.5,
            borderColor=self.colors['border'],
            fillColor=self.colors['background'],
            textColor=self.colors['primary'],
            fieldFlags=0
        )

        final_field_y = field_y_position - self.field_height - 10

        # Update positioning with adequate spacing
        if self.generator.current_group is not None:
            self._handle_group_positioning(field_x, field_width, final_field_y, starting_y)
        else:
            self.generator.current_y = final_field_y - 8  # Adequate spacing

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
            
            # Calculate X position
            field_x = self.margin_x
            if column_index > 0:
                field_x += sum(self.generator.column_widths[:column_index])
                field_x += self.generator.group_spacing * column_index
            
            # CRITICAL: Use the actual column width
            field_width = self.generator.column_widths[column_index]
            
            # Align rows properly
            if column_index > 0 and self.generator.group_fields:
                row_index = group_index // self.generator.group_columns
                first_in_row_index = row_index * self.generator.group_columns
                if first_in_row_index < len(self.generator.group_fields):
                    first_field = self.generator.group_fields[first_in_row_index]
                    field_y = first_field.get('start_y', first_field.get('y', field_y))

        print(f"DEBUG _get_field_position: field_x={field_x}, field_width={field_width}, field_y={field_y}")
        return field_x, field_width, field_y

    def _handle_group_positioning(self, field_x, field_width, final_y, start_y):
        """Handle positioning when field is in a group"""
        self.generator.group_fields.append({
            'name': 'text_field',
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