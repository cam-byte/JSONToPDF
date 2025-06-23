# fields/group_field.py - SIMPLE VERSION WITHOUT NESTING SUPPORT
class GroupField:
    def __init__(self, generator, canvas):
        self.generator = generator
        self.canvas = canvas
        self.margin_x = generator.margin_x
        self.field_width = generator.field_width
        self.colors = generator.colors

    def start_group(self, group_name):
        # List of groups that should be ignored when nested
        ignored_nested_groups = {'substance_details', 'women_only'}
        
        if(group_name == 'name_details' or group_name == '*name_details'):
            print(f"name_details group started")
        
        if self.generator.current_group is not None:
            return
        
        self.generator.current_group = group_name
        self.generator.group_fields = []
        # Store the starting Y position
        self.generator.group_start_y = self.generator.current_y
        
        # Get group configuration
        config = self.generator.group_configs.get(group_name, {
            'columns': 2,
            'widths': [0.5, 0.5],
            'spacing': 15
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
        
        # Calculate actual pixel widths with proper spacing
        total_spacing = spacing * (columns - 1) if columns > 1 else 0
        available_width = self.field_width - total_spacing
        
        self.generator.column_widths = [
            width * available_width for width in widths
        ]
        self.generator.group_spacing = spacing
        self.generator.group_columns = columns

    def end_group(self):
        # If the current group is None (already ended or ignored), do nothing
        if self.generator.current_group is None:
            return
        
        if self.generator.group_fields:
            # Enhanced row alignment logic for text wrapping
            self._align_group_rows()
        
        # Reset group variables
        self.generator.current_group = None
        self.generator.group_fields = []
        self.generator.column_widths = None
        self.generator.group_spacing = None
        self.generator.group_columns = None
        self.generator.group_start_y = None

    def _align_group_rows(self):
        """Align fields in rows properly, accounting for text wrapping"""
        if not self.generator.group_fields:
            return
        
        columns = self.generator.group_columns
        rows = {}
        
        # Group fields by row
        for i, field in enumerate(self.generator.group_fields):
            row_index = i // columns
            if row_index not in rows:
                rows[row_index] = []
            rows[row_index].append(field)
        
        # Process each row to find the lowest Y position
        final_y = self.generator.group_start_y
        
        for row_index, row_fields in rows.items():
            if row_fields:
                # Find the lowest Y position in this row
                row_min_y = min(f.get('y', self.generator.group_start_y) for f in row_fields)
                final_y = min(final_y, row_min_y)
        
        # Set the final Y position with adequate spacing
        self.generator.current_y = final_y - 20

    def get_column_info(self, column_index):
        """Get positioning info for a specific column"""
        if (self.generator.current_group is None or
            not hasattr(self.generator, 'column_widths') or
            column_index >= len(self.generator.column_widths)):
            return self.margin_x, self.field_width
        
        field_x = self.margin_x
        if column_index > 0:
            field_x += sum(self.generator.column_widths[:column_index])
            field_x += self.generator.group_spacing * column_index
        
        field_width = self.generator.column_widths[column_index]
        return field_x, field_width