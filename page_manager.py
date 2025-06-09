# page_manager.py
from reportlab.lib.utils import ImageReader
from utils import _strip_html_tags, _wrap_text, _prepare_logo_image

class PageManager:
    def __init__(self, generator):
        self.generator = generator
        
    def initialize_page(self, canvas):
        width, height = self.generator.page_width, self.generator.page_height
        
        header_height = 75
        scaled_height = 75
        
        img_reader, original_size = _prepare_logo_image(self.generator.logo_path)
        if img_reader and original_size:
            try:
                original_width, original_height = original_size
                fixed_width = 100
                fixed_height = 75

                scale_factor = min(fixed_width / original_width, fixed_height / original_height)
                scaled_width = original_width * scale_factor
                scaled_height = original_height * scale_factor

                canvas.drawImage(img_reader, 
                           (width - scaled_width) / 2, 
                           height - scaled_height - 20, 
                           width=scaled_width, 
                           height=scaled_height)
                
                header_height = scaled_height + 85 + 20
            except Exception as e:
                print(f"Error drawing logo: {str(e)}")
        
        canvas.setFillColor(self.generator.colors['primary'])
        canvas.setFont("Helvetica", 8)
        
        y_offset = height - scaled_height - 40
        canvas.drawCentredString(width / 2, y_offset, self.generator.business_name)
        canvas.drawCentredString(width / 2, y_offset - 15, self.generator.address)
        canvas.drawCentredString(width / 2, y_offset - 30, self.generator.phone)
        canvas.drawCentredString(width / 2, y_offset - 45, self.generator.email)

        self.generator.current_y = height - header_height - 20
        canvas.setFont("Helvetica", 10)

    def draw_page_number(self, canvas, current_page, total_pages):
        current_font = canvas._fontname
        current_size = canvas._fontsize
        current_color = canvas._fillColorObj

        canvas.setFont("Helvetica", 9)
        canvas.setFillColor(self.generator.colors['secondary'])
        canvas.drawString(
            self.generator.page_width - self.generator.margin_x - 40,
            self.generator.margin_bottom - 20,
            f"Page {current_page} of {total_pages}"
        )

        canvas.setFont(current_font, current_size)
        canvas.setFillColor(current_color)