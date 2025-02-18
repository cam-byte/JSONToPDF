# label_manager.py
from utils import _strip_html_tags, _wrap_text
class LabelManager:
    def __init__(self, generator):
        self.generator = generator

    def get_label_style(self, field_type, label):
        if field_type == 'label':
            has_html = '<h1>' in label.lower() or '<h3>' in label.lower() or '<h4>' in label.lower() or '<p>' in label.lower()
            if has_html:
                if '<h1>' in label.lower():
                    return self.generator.label_styles['h1']
                elif '<h3>' in label.lower():
                    return self.generator.label_styles['h3']
                elif '<h4>' in label.lower():
                    return self.generator.label_styles['h4']
                elif '<p>' in label.lower():
                    return self.generator.label_styles['p']
            return self.generator.label_styles['regular']
        return self.generator.label_styles['field_label']

    def draw_label(self, canvas, text, style, draw_line=False):
        current_font = canvas._fontname
        current_size = canvas._fontsize
        current_color = canvas._fillColorObj
        
        try:
            canvas.setFont(style.font_name, style.font_size)
            canvas.setFillColor(style.color)
        except Exception as e:
            print(f"Error setting font {style.font_name}: {str(e)}")
        
        clean_text = _strip_html_tags(text)
        wrapped_lines = _wrap_text(clean_text, self.generator.field_width - 40)
        
        for i, line in enumerate(wrapped_lines):
            if style.alignment == 'center':
                text_width = canvas.stringWidth(line, style.font_name, style.font_size)
                x_position = (self.generator.page_width - text_width) / 2
            else:
                x_position = self.generator.margin_x
                
            canvas.drawString(x_position, self.generator.current_y, line)
            if i < len(wrapped_lines) - 1:
                self.generator.current_y -= 15
        
        if draw_line:
            self.generator.current_y -= 10
            canvas.setLineWidth(0.5)
            canvas.setStrokeColor(self.generator.colors['border'])
            canvas.line(self.generator.margin_x, self.generator.current_y,
                self.generator.margin_x + self.generator.field_width, self.generator.current_y)
        
        self.generator.current_y -= style.spacing_after

        canvas.setFont(current_font, current_size)
        canvas.setFillColor(current_color)