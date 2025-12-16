# page_manager.py - HEADER ONLY ON FIRST PAGE
from utils import _prepare_logo_image, _calculate_logo_dimensions

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
            # Get the actual Y position after header is drawn
            header_end_y = self._draw_clean_business_header(canvas)
            # Set current_y to just below the header with extra spacing for main title
            self.generator.current_y = header_end_y - 30
        else:
            # Less space from top on subsequent pages
            self.generator.current_y -= 15

    def _draw_clean_business_header(self, canvas):
        """Draw clean, professional business header (first page only)

        Returns:
            float: The Y position after the header (position of the bottom line)
        """
        current_font = canvas._fontname
        current_size = canvas._fontsize
        current_color = canvas._fillColorObj

        # Header positioning
        header_y = self.page_height - 25

        # Draw logo centered on its own row at the top if available
        logo_height = 0
        if self.generator.logo_path:
            logo_img = _prepare_logo_image(self.generator.logo_path)
            if logo_img:
                logo_width, logo_height = _calculate_logo_dimensions(
                    self.generator.logo_path,
                    max_width=120,
                    max_height=50
                )
                # Center the logo horizontally
                logo_x = (self.page_width - logo_width) / 2
                # Draw logo at the top
                canvas.drawImage(
                    logo_img,
                    logo_x,
                    header_y - logo_height,
                    width=logo_width,
                    height=logo_height,
                    preserveAspectRatio=True,
                    mask='auto'
                )
                # Adjust header_y to position text below the logo
                header_y = header_y - logo_height - 15

        # Business name on the left
        canvas.setFont("Helvetica-Bold", 11)
        canvas.setFillColor(self.colors['primary'])
        canvas.drawString(self.margin_x, header_y, self.generator.business_name)

        # Address on second line (left side)
        canvas.setFont("Helvetica", 9)
        canvas.drawString(self.margin_x, header_y - 12, self.generator.address)

        # Contact info on the right, right-aligned
        canvas.setFont("Helvetica", 9)
        # Only add dot separator if email exists
        if self.generator.email:
            contact_info = f"{self.generator.phone} • {self.generator.email}"
        else:
            contact_info = self.generator.phone
        text_width = canvas.stringWidth(contact_info, "Helvetica", 9)
        canvas.drawString(self.page_width - self.margin_x - text_width, header_y, contact_info)

        # Optional: Add a subtle line under the header
        canvas.setStrokeColor(self.colors['border'])
        canvas.setLineWidth(0.5)
        line_y = header_y - 18
        canvas.line(self.margin_x, line_y,
                   self.page_width - self.margin_x, line_y)

        # Restore original font settings
        canvas.setFont(current_font, current_size)
        canvas.setFillColor(current_color)

        # Return the Y position after the header line
        return line_y