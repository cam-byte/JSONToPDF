# fields/text_area.py
class TextArea:
    def __init__(self, generator, canvas):
        self.generator = generator
        self.canvas = canvas
        self.colors = generator.colors
        self.margin_x = generator.margin_x
        self.field_width = generator.field_width
        self.field_height = generator.field_height

    def draw(self, field_name, label):
        field_x = self.margin_x
        field_width = self.field_width
        
        if self.generator.current_group is not None:
            group_index = len(self.generator.group_fields)
            column_index = group_index % self.generator.group_columns
            
            # Calculate x position
            field_x = self.margin_x
            if column_index > 0:
                # Add widths of previous columns plus spacing
                field_x += sum(self.generator.column_widths[:column_index])
                field_x += self.generator.group_spacing * column_index
            
            field_width = self.generator.column_widths[column_index]
            
            # If not first in row, align with previous field's y position
            if column_index > 0:
                previous_field = self.generator.group_fields[group_index - 1]
                self.generator.current_y = previous_field['y']
        
        textarea_height = 100
        self.canvas.acroForm.textfield(
            name=field_name,
            tooltip=label,
            x=self.margin_x,
            y=self.generator.current_y - textarea_height,
            width=self.field_width,
            height=100,
            fontSize=10,
            borderWidth=0.5,
            borderColor=self.colors['border'],
            fillColor=self.colors['background'],
            textColor=self.colors['primary'],
            fieldFlags=4096
        )
        
        self.generator.current_y -= (textarea_height + 10)
        
        # Store field info for group positioning
        if self.generator.current_group is not None:
            self.generator.group_fields.append({
                'name': field_name,
                'x': field_x,
                'y': self.generator.current_y,
                'width': field_width
            })
        
        # Move to next line only if last in row or not in a group
        if (not self.generator.current_group or 
            (len(self.generator.group_fields) % self.generator.group_columns == 0)):
            self.generator.current_y -= (self.field_height + 25)