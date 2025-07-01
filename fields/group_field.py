# fields/group_field.py - ENHANCED WITH SMART GROUP OVERRIDE LOGIC

class GroupField:
    def __init__(self, generator, canvas):
        self.generator = generator
        self.canvas = canvas
        self.margin_x = generator.margin_x
        self.field_width = generator.field_width
        self.colors = generator.colors
        
        # Define group hierarchy
        self.container_groups = {
            'form_container',
            'form_content_container', 
            'primary_insurance',
            'secondary_insurance',
            'permanent',
            'deciduous',
            'top_row',
            'bottom_row',
            'tooth_container',
            'indent_x1',
            'substance_details',
            'pharmacy_information'
        }
        
        self.functional_groups = {
            'name_details',
            'address_details', 
            'patient_contact',
            'phone_details',
            'two_columns',
            'four_columns',
            'women_only',
            'tooth',
            'contact_information'
        }

    def start_group(self, group_name):
        """Start a group with smart nesting logic"""
        clean_group_name = group_name.lstrip('*')  # Remove any prefix markers
        
        # Determine group types
        is_container = clean_group_name in self.container_groups
        is_functional = clean_group_name in self.functional_groups
        
        
        # Smart nesting logic
        if self.generator.current_group is not None:
            current_is_container = self.generator.current_group in self.container_groups
            current_is_functional = self.generator.current_group in self.functional_groups
            
            
            # Rule 1: Functional groups can override container groups
            if is_functional and current_is_container:
                self._end_current_group_silently()
            
            # Rule 2: Prevent functional group nesting
            elif is_functional and current_is_functional:
                return
            
            # Rule 3: Container groups are ignored when already in functional groups
            elif is_container and current_is_functional:
                return
            
            # Rule 4: Container groups can nest within other container groups
            elif is_container and current_is_container:
                # Allow container nesting, but don't actually change active group
                return
            
            # Rule 5: Unknown groups default to blocking
            else:
                return
        
        # Start the new group
        self._initialize_group(clean_group_name)
        
    def _end_current_group_silently(self):
        """End current group without drawing/alignment (used for overrides)"""
        self.generator.current_group = None
        self.generator.group_fields = []
        self.generator.column_widths = None
        self.generator.group_spacing = None
        self.generator.group_columns = None
        self.generator.group_start_y = None
        
    def _initialize_group(self, group_name):
        """Initialize a new group with proper configuration"""
        self.generator.current_group = group_name
        self.generator.group_fields = []
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
        """End the current group with proper cleanup and alignment"""
        # If no current group, nothing to do
        if self.generator.current_group is None:
            return
        
        group_name = self.generator.current_group
        
        # Only align if we have functional group fields that need positioning
        is_functional = group_name in self.functional_groups
        if is_functional and self.generator.group_fields:
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
        
        group_name = self.generator.current_group
        
        # Calculate appropriate spacing based on group content
        if group_name == 'women_only':
            # Women Only group needs extra spacing due to radio buttons and text
            additional_spacing = 30
        elif any(field.get('name', '').startswith('radio') or 'radio' in str(field) for field in self.generator.group_fields):
            # Groups with radio buttons need more spacing
            additional_spacing = 20
        else:
            # Default spacing for other groups
            additional_spacing = 15
        
        final_position = final_y - additional_spacing
        self.generator.current_y = final_position

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

    def is_functional_group(self, group_name=None):
        """Check if a group is functional (controls layout)"""
        target_group = group_name or self.generator.current_group
        if target_group is None:
            return False
        return target_group.lstrip('*') in self.functional_groups
        
    def is_container_group(self, group_name=None):
        """Check if a group is a container (organizational only)"""
        target_group = group_name or self.generator.current_group
        if target_group is None:
            return False
        return target_group.lstrip('*') in self.container_groups