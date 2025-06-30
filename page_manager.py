# page_manager.py - HEADER ONLY ON FIRST PAGE
from utils import _prepare_logo_image

class PageManager:
    def __init__(self, generator):
        self.generator = generator
        self.colors = generator.colors
        self.page_width = generator.page_width
        self.page_height = generator.page_height
        self.margin_x = generator.margin_x

    def initialize_page(self, canvas):
        """Initialize a new page with conditional header"""
        # Reset Y position to top of page
        self.generator.current_y = self.page_height - self.margin_x
        
        # Only draw business header on first page
        if self.generator.current_page == 1:
            self._draw_clean_business_header(canvas)
            # More space after business header on first page
            self.generator.current_y -= 35
        else:
            # Less space from top on subsequent pages
            self.generator.current_y -= 15

    def _draw_clean_business_header(self, canvas):
        """Draw clean, professional business header (first page only)"""
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
        
        # Optional: Add a subtle line under the header
        canvas.setStrokeColor(self.colors['border'])
        canvas.setLineWidth(0.5)
        canvas.line(self.margin_x, header_y - 18, 
                   self.page_width - self.margin_x, header_y - 18)
        
        # Restore original font settings
        canvas.setFont(current_font, current_size)
        canvas.setFillColor(current_color)