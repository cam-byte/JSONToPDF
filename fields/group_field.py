# fields/group_field.py - Simplified version
class GroupField:
    def __init__(self, generator, canvas):
        self.generator = generator
        self.canvas = canvas
        self.margin_x = generator.margin_x
        self.field_width = generator.field_width
        self.colors = generator.colors

    def start_group(self, group_name):
        self.generator.current_group = group_name
        self.generator.group_fields = []
        
        # Get group configuration
        config = self.generator.group_configs.get(group_name, {
            'columns': 1,
            'widths': [1.0],
            'spacing': 10
        })
        
        columns = config['columns']
        widths = config['widths']
        spacing = config['spacing']
        
        # Ensure we have the right number of widths
        if len(widths) != columns:
            # Fix it by extending or truncating
            if len(widths) < columns:
                # Add equal remaining width
                remaining = 1.0 - sum(widths)
                additional = remaining / (columns - len(widths))
                widths.extend([additional] * (columns - len(widths)))
            else:
                widths = widths[:columns]
        
        # Normalize widths to proportions (handle both decimal and integer formats)
        total = sum(widths)
        if total == 0:
            widths = [1.0 / columns] * columns
        else:
            widths = [w / total for w in widths]
        
        # Calculate actual pixel widths
        total_spacing = spacing * (columns - 1) if columns > 1 else 0
        available_width = self.field_width - total_spacing
        
        self.generator.column_widths = [
            width * available_width for width in widths
        ]
        self.generator.group_spacing = spacing
        self.generator.group_columns = columns
        
        return self.generator.current_y

    def end_group(self):
        if self.generator.group_fields:
            # Find the lowest Y position from all fields
            min_y = min(f['y'] for f in self.generator.group_fields)
            self.generator.current_y = min_y - (self.generator.field_height + 25)
        
        print(f"Ended group {self.generator.current_group}, new Y: {self.generator.current_y}")

        # Reset group variables
        self.generator.current_group = None
        self.generator.group_fields = []
        self.generator.column_widths = None
        self.generator.group_spacing = None
        self.generator.group_columns = None
        
        return self.generator.current_y

    def get_field_position(self, field_index):
        """Calculate position for field within group"""
        if not self.generator.current_group:
            return self.margin_x, self.field_width, self.generator.current_y
        
        column_index = field_index % self.generator.group_columns
        row_index = field_index // self.generator.group_columns
        
        # Calculate X position
        field_x = self.margin_x
        if column_index > 0:
            # Add widths of previous columns plus spacing
            field_x += sum(self.generator.column_widths[:column_index])
            field_x += self.generator.group_spacing * column_index
        
        field_width = self.generator.column_widths[column_index]
        
        # For Y position: all fields in the same row should have the same Y
        if column_index == 0:
            # First column - use current Y
            field_y = self.generator.current_y
        else:
            # Not first column - find the Y of the first field in this row
            first_in_row_index = row_index * self.generator.group_columns
            if first_in_row_index < len(self.generator.group_fields):
                field_y = self.generator.group_fields[first_in_row_index]['y']
            else:
                field_y = self.generator.current_y
        
        print(f"Field {field_index} -> Column {column_index}: x={field_x:.0f}, width={field_width:.0f}, y={field_y}")
        
        return field_x, field_width, field_y