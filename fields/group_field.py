# fields/group_field.py - SIMPLIFIED AND FIXED

class GroupField:
    def __init__(self, generator, canvas):
        self.generator = generator
        self.canvas = canvas
        self.margin_x = generator.margin_x
        self.field_width = generator.field_width
        self.colors = generator.colors
        
        # Simplified group types - only track functional layout groups
        self.layout_groups = {
            'two_columns': {'columns': 2, 'widths': [0.48, 0.48], 'spacing': 20},
            'four_columns': {'columns': 4, 'widths': [0.22, 0.22, 0.22, 0.22], 'spacing': 15},
            'name_details': {'columns': 2, 'widths': [0.6, 0.4], 'spacing': 15},
            'address_details': {'columns': 3, 'widths': [0.4, 0.3, 0.3], 'spacing': 12},
            'patient_contact': {'columns': 2, 'widths': [0.5, 0.5], 'spacing': 15},
            'phone_details': {'columns': 3, 'widths': [0.33, 0.33, 0.33], 'spacing': 10},
        }
        
        # Container groups that we ignore for layout purposes
        self.container_groups = {
            'form_container', 'form_content_container', 'primary_insurance', 
            'secondary_insurance', 'permanent', 'deciduous', 'top_row', 
            'bottom_row', 'tooth_container', 'indent_x1', 'substance_details', 
            'pharmacy_information'
        }

    def start_group(self, group_name):
        """Simplified group start - only handle layout groups"""
        clean_group_name = group_name.lstrip('*')
        
        # If this is a container group, ignore it
        if clean_group_name in self.container_groups:
            return
            
        # If we're already in a layout group, end it first
        if self.generator.current_group is not None:
            self.end_group()
        
        # Only start if this is a recognized layout group
        if clean_group_name in self.layout_groups:
            self._initialize_group(clean_group_name)
        
    def _initialize_group(self, group_name):
        """Initialize a layout group with proper configuration"""
        self.generator.current_group = group_name
        self.generator.group_fields = []
        self.generator.group_start_y = self.generator.current_y
        
        config = self.layout_groups[group_name]
        columns = config['columns']
        widths = config['widths']
        spacing = config['spacing']
        
        # Calculate actual pixel widths
        total_spacing = spacing * (columns - 1) if columns > 1 else 0
        available_width = self.field_width - total_spacing
        
        self.generator.column_widths = [
            width * available_width for width in widths
        ]
        self.generator.group_spacing = spacing
        self.generator.group_columns = columns

    def end_group(self):
        """End the current group and align fields properly"""
        if self.generator.current_group is None:
            return
        
        # Calculate the final Y position based on all fields in the group
        if self.generator.group_fields:
            # Find the lowest Y position among all fields
            min_y = min(field.get('y', self.generator.current_y) for field in self.generator.group_fields)
            # Add some spacing after the group
            self.generator.current_y = min_y - 15
        
        # Reset group state
        self.generator.current_group = None
        self.generator.group_fields = []
        self.generator.column_widths = None
        self.generator.group_spacing = None
        self.generator.group_columns = None
        self.generator.group_start_y = None

    def get_field_position_in_group(self):
        """Get the position for the next field in the current group"""
        if self.generator.current_group is None:
            return self.margin_x, self.field_width, self.generator.current_y
        
        group_index = len(self.generator.group_fields)
        column_index = group_index % self.generator.group_columns
        row_index = group_index // self.generator.group_columns
        
        # Calculate X position
        field_x = self.margin_x
        if column_index > 0:
            field_x += sum(self.generator.column_widths[:column_index])
            field_x += self.generator.group_spacing * column_index
        
        field_width = self.generator.column_widths[column_index]
        
        # Calculate Y position - use row-based positioning
        field_y = self.generator.group_start_y
        if row_index > 0:
            # For subsequent rows, look at the previous row's minimum Y
            prev_row_start = (row_index - 1) * self.generator.group_columns
            prev_row_end = min(prev_row_start + self.generator.group_columns, len(self.generator.group_fields))
            if prev_row_end > prev_row_start:
                prev_row_fields = self.generator.group_fields[prev_row_start:prev_row_end]
                prev_row_min_y = min(f.get('y', field_y) for f in prev_row_fields)
                field_y = prev_row_min_y - 35  # Row spacing
        
        return field_x, field_width, field_y

    def add_field_to_group(self, field_name, final_y, start_y=None, field_x=None, field_width=None):
        """Add a field to the current group tracking"""
        if self.generator.current_group is None:
            return
            
        self.generator.group_fields.append({
            'name': field_name,
            'y': final_y,
            'start_y': start_y or final_y,
            'x': field_x or self.margin_x,
            'width': field_width or self.field_width
        })