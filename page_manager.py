# page_manager.py - CLEAN HEADER LAYOUT
from utils import _prepare_logo_image

class PageManager:
    def __init__(self, generator):
        self.generator = generator
        self.colors = generator.colors
        self.page_width = generator.page_width
        self.page_height = generator.page_height
        self.margin_x = generator.margin_x

    def initialize_page(self, canvas):
        """Initialize a new page with clean header"""
        # Reset Y position to top of page
        self.generator.current_y = self.page_height - self.margin_x
        
        # Draw clean business header
        self._draw_clean_business_header(canvas)
        
        # Reasonable space after business header
        self.generator.current_y -= 35

    def _draw_clean_business_header(self, canvas):
        """Draw clean, professional business header"""
        current_font = canvas._fontname
        current_size = canvas._fontsize
        current_color = canvas._fillColorObj
        
        # Header positioning
        header_y = self.page_height - 25
        
        # Business name and contact info on same line
        canvas.setFont("Helvetica-Bold", 11)
        canvas.setFillColor(self.colors['primary'])
        canvas.drawString(self.margin_x, header_y, self.generator.business_name)
        
        # Contact info on same line, right-aligned
        canvas.setFont("Helvetica", 9)
        contact_info = f"{self.generator.phone} • {self.generator.email}"
        text_width = canvas.stringWidth(contact_info, "Helvetica", 9)
        canvas.drawString(self.page_width - self.margin_x - text_width, header_y, contact_info)
        
        # Address on second line
        canvas.setFont("Helvetica", 9)
        canvas.drawString(self.margin_x, header_y - 12, self.generator.address)
        
        # Restore original font settings
        canvas.setFont(current_font, current_size)
        canvas.setFillColor(current_color)

    def draw_page_number(self, canvas, current_page, total_pages):
        """Draw page number at bottom right"""
        current_font = canvas._fontname
        current_size = canvas._fontsize
        current_color = canvas._fillColorObj
        
        canvas.setFont("Helvetica", 9)
        canvas.setFillColor(self.colors['secondary'])
        page_text = f"Page {current_page} of {total_pages}"
        text_width = canvas.stringWidth(page_text, "Helvetica", 9)
        canvas.drawString(
            self.page_width - self.margin_x - text_width,
            25,
            page_text
        )
        
        canvas.setFont(current_font, current_size)
        canvas.setFillColor(current_color)