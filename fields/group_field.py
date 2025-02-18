# fields/group_field.py
class GroupField:
    def __init__(self, generator, canvas):
        self.generator = generator
        self.canvas = canvas
        self.margin_x = generator.margin_x
        self.field_width = generator.field_width
        self.colors = generator.colors

    def _normalize_widths(self, widths):
        """Normalize widths to ensure they sum to 1.0"""
        total = sum(widths)
        if total == 0:
            # If all widths are 0, make them equal
            return [1.0 / len(widths)] * len(widths)
        return [width / total for width in widths]

    def start_group(self, group_name):
        self.generator.current_group = group_name
        self.generator.group_fields = []
        
        # Get group configuration with defaults
        config = self.generator.group_configs.get(group_name, {
            'columns': 1,
            'widths': [1.0],
            'spacing': 10
        })
        
        # Ensure widths match number of columns
        columns = config['columns']
        widths = config['widths']
        if len(widths) != columns:
            widths = widths[:columns] if len(widths) > columns else widths + [widths[-1]] * (columns - len(widths))
        
        # Normalize widths to ensure they sum to 1.0
        normalized_widths = self._normalize_widths(widths)
        
        # Calculate actual pixel widths including spacing
        spacing = config['spacing']
        total_spacing = spacing * (columns - 1)
        available_width = self.field_width - total_spacing
        
        self.generator.column_widths = [
            width * available_width for width in normalized_widths
        ]
        self.generator.group_spacing = spacing
        self.generator.group_columns = columns
        
        return self.generator.current_y

    def end_group(self):
        if self.generator.group_fields:
            last_row_index = (len(self.generator.group_fields) - 1) // self.generator.group_columns
            last_row_fields = [f for i, f in enumerate(self.generator.group_fields) 
                             if i // self.generator.group_columns == last_row_index]
            if last_row_fields:
                self.generator.current_y = min(f['y'] for f in last_row_fields)
                self.generator.current_y -= (self.generator.field_height + 25)

        self.generator.current_group = None
        self.generator.group_fields = []
        self.generator.column_widths = None
        self.generator.group_spacing = None
        self.generator.group_columns = None
        
        return self.generator.current_y