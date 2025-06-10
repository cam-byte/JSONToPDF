# fields/group_field.py - COMPACT VERSION
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
        
        # Store the starting Y position
        self.generator.group_start_y = self.generator.current_y
        
        # Get group configuration
        config = self.generator.group_configs.get(group_name, {
            'columns': 2,
            'widths': [0.5, 0.5],
            'spacing': 10  # Default reduced spacing
        })
        
        columns = config['columns']
        widths = config['widths']
        spacing = config['spacing']
        
        # Ensure we have the right number of widths
        if len(widths) != columns:
            widths = [1.0 / columns] * columns
        
        # Normalize widths to proportions
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

    def end_group(self):
        if self.generator.group_fields:
            # Group fields by row and find the lowest Y position
            rows = {}
            for i, field in enumerate(self.generator.group_fields):
                row_index = i // self.generator.group_columns
                if row_index not in rows:
                    rows[row_index] = []
                rows[row_index].append(field)
            
            # Find the lowest Y position across all rows
            lowest_y = self.generator.group_start_y
            for row_fields in rows.values():
                row_min_y = min(f.get('y', self.generator.current_y) for f in row_fields)
                lowest_y = min(lowest_y, row_min_y)
            
            # Set Y position with minimal spacing after group
            self.generator.current_y = lowest_y - 5  # Reduced from 10
        
        # Reset group variables
        self.generator.current_group = None
        self.generator.group_fields = []
        self.generator.column_widths = None
        self.generator.group_spacing = None
        self.generator.group_columns = None
        self.generator.group_start_y = None