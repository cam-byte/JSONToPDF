# fields/text_area.py
class TextArea:
    def __init__(self, generator, canvas):
        self.generator = generator
        self.canvas = canvas
        self.colors = generator.colors
        self.margin_x = generator.margin_x
        self.field_width = generator.field_width

    def draw(self, field_name, label):
        c = self.canvas
        textarea_height = 100
        c.acroForm.textfield(
            name=field_name,
            tooltip=label,
            x=self.margin_x,
            y=self.generator.current_y - textarea_height,
            width=self.field_width,
            height=textarea_height,
            fontSize=10,
            borderWidth=0.5,
            borderColor=self.colors['border'],
            fillColor=self.colors['background'],
            textColor=self.colors['primary'],
            fieldFlags=4096
        )
        self.generator.current_y -= (textarea_height + 20)