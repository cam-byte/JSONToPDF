# fields/text_field.py - ENHANCED WITH DEBUGGING
from utils import _check_page_break, draw_wrapped_text, calculate_wrapped_text_height, get_effective_field_width, create_acrobat_compatible_field

class TextField:
    def __init__(self, generator, canvas):
        self.generator = generator
        self.canvas = canvas
        self.colors = generator.colors
        self.margin_x = generator.margin_x
        self.field_width = generator.field_width
        self.field_height = generator.field_height

    def draw(self, field_name, label):
        print(f"📝 Drawing text field: '{field_name}' with label: '{label}'")
        print(f"   Current group: {self.generator.current_group}")
        
        c = self.canvas
        current_font = c._fontname
        current_size = c._fontsize
        current_color = c._fillColorObj

        # Calculate field positioning
        field_x, field_width, field_y = self._get_field_position()
        starting_y = field_y
        
        print(f"   📍 Position: x={field_x}, width={field_width}, y={field_y}")
        
        # Draw label with text wrapping using ACTUAL field width
        if label:
            field_label_style = self.generator.label_styles['field_label']
            
            # CRITICAL FIX: Use actual field width, not page width
            max_label_width = field_width * 0.88  # Use 88% of the actual column width
            
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
            field_y = final_label_y + 7  # Space between label and field

        # Position field below label
        field_y_position = field_y

        # Draw text field - THE KEY FIX IS HERE
        create_acrobat_compatible_field(c, 'textfield',
            name=field_name,
            tooltip=label,
            x=field_x,
            y=field_y_position - self.field_height,
            width=field_width,
            height=self.field_height,
            fontSize=10,
            fieldFlags=0
        )

        final_field_y = field_y_position - self.field_height - 10

        # Update positioning with adequate spacing
        if self.generator.current_group is not None:
            print(f"   📋 Adding to group (index {len(self.generator.group_fields)})")
            self._handle_group_positioning(field_x, field_width, final_field_y, starting_y)
        else:
            print(f"   📍 Not in group, updating current_y to {final_field_y - 8}")
            self.generator.current_y = final_field_y - 8  # Adequate spacing

        c.setFont(current_font, current_size)
        c.setFillColor(current_color)
        
        print(f"   ✅ Text field '{field_name}' completed")

    def _get_field_position(self):
        """Calculate position for field within group or regular flow"""
        field_x = self.margin_x
        field_width = self.field_width  # Default to full width
        field_y = self.generator.current_y

        # Only adjust if we're in a group AND have proper group configuration
        if (self.generator.current_group is not None and 
            hasattr(self.generator, 'group_columns') and 
            self.generator.group_columns is not None and
            hasattr(self.generator, 'column_widths') and 
            self.generator.column_widths is not None):
            
            group_index = len(self.generator.group_fields)
            column_index = group_index % self.generator.group_columns
            
            print(f"   🔢 Group calculations: index={group_index}, column={column_index}, total_columns={self.generator.group_columns}")
            
            # Calculate X position
            field_x = self.margin_x
            if column_index > 0:
                field_x += sum(self.generator.column_widths[:column_index])
                field_x += self.generator.group_spacing * column_index
            
            # CRITICAL: Use the actual column width instead of full page width
            field_width = self.generator.column_widths[column_index]
            
            print(f"   📏 Column {column_index}: x={field_x}, width={field_width}")
            
            # Align rows properly
            if column_index > 0 and self.generator.group_fields:
                row_index = group_index // self.generator.group_columns
                first_in_row_index = row_index * self.generator.group_columns
                if first_in_row_index < len(self.generator.group_fields):
                    first_field = self.generator.group_fields[first_in_row_index]
                    field_y = first_field.get('start_y', first_field.get('y', field_y))
                    print(f"   📐 Row alignment: using y={field_y} from first field in row")
        else:
            print(f"   📍 Not in valid group - using full width. Group: {self.generator.current_group}, Columns: {getattr(self.generator, 'group_columns', 'None')}")

        return field_x, field_width, field_y

    def _handle_group_positioning(self, field_x, field_width, final_y, start_y):
        """Handle positioning when field is in a group"""
        field_info = {
            'name': 'text_field',
            'x': field_x,
            'y': final_y,
            'start_y': start_y,
            'width': field_width
        }
        
        self.generator.group_fields.append(field_info)
        print(f"   📋 Added field to group: {field_info}")

        # Only check for row completion if we have valid group configuration
        if (hasattr(self.generator, 'group_columns') and 
            self.generator.group_columns is not None and 
            len(self.generator.group_fields) % self.generator.group_columns == 0):
            
            row_start = len(self.generator.group_fields) - self.generator.group_columns
            row_fields = self.generator.group_fields[row_start:]
            min_y = min(f.get('y', self.generator.current_y) for f in row_fields)
            self.generator.current_y = min_y - 8
            print(f"   📐 Row completed, updated current_y to: {self.generator.current_y}")
        else:
            print(f"   📋 Field added to group, waiting for more fields or invalid group config")