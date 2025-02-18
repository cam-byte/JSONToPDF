# fields/text_field.py
class TextField:
    def __init__(self, generator, canvas):
        self.generator = generator
        self.canvas = canvas
        self.colors = generator.colors
        self.margin_x = generator.margin_x
        self.field_width = generator.field_width
        self.field_height = generator.field_height

    def draw(self, field_name, label, options=None):
        c = self.canvas
        c.acroForm.textfield(
            name=field_name,
            tooltip=label,
            x=self.margin_x,
            y=self.generator.current_y - self.field_height,
            width=self.field_width,
            height=self.field_height,
            fontSize=10,
            borderWidth=0.5,
            borderColor=self.colors['border'],
            fillColor=self.colors['background'],
            textColor=self.colors['primary'],
            fieldFlags=0
        )
        self.generator.current_y -= (self.field_height + 25)