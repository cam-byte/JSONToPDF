from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.utils import simpleSplit
from reportlab.lib.utils import ImageReader
from reportlab.lib import colors
from PIL import Image
import io
import json
import os
import re

class LabelStyle:
    def __init__(self, font_name, font_size, color, spacing_after, alignment='left'):
        self.font_name = font_name
        self.font_size = font_size
        self.color = color
        self.spacing_after = spacing_after
        self.alignment = alignment

class ModernPDFFormGenerator:
    def __init__(self, json_data):
        self.data = json_data
        self.page_width, self.page_height = letter
        
        # Register fonts
        pdfmetrics.registerFont(pdfmetrics.Font('Helvetica', 'Helvetica', 'WinAnsiEncoding'))
        pdfmetrics.registerFont(pdfmetrics.Font('Helvetica-Bold', 'Helvetica-Bold', 'WinAnsiEncoding'))
        pdfmetrics.registerFont(pdfmetrics.Font('Helvetica-Oblique', 'Helvetica-Oblique', 'WinAnsiEncoding'))
        pdfmetrics.registerFont(pdfmetrics.Font('Helvetica-BoldOblique', 'Helvetica-BoldOblique', 'WinAnsiEncoding'))
        
        self.margin_x = 72
        self.margin_bottom = 72
        self.current_y = self.page_height - 72
        self.field_width = 450
        self.field_height = 24
        self.current_page = 1
        self.logo_path = '/Users/camerondyas/Documents/scripts/pythonScripts/JSONToPDF/form/logo.png'
        self.address = '123 Main St, Anytown, USA 12345'
        self.phone = '(555) 555-5555'
        self.email = 'contact@business.com'
        self.business_name = 'Business Name'
        self.colors = {
            'primary': colors.HexColor('#2D3748'),
            'secondary': colors.HexColor('#4A5568'),
            'accent': colors.HexColor('#3182CE'),
            'border': colors.HexColor('#E2E8F0'),
            'background': colors.HexColor('#F7FAFC'),
        }
        self.label_styles = {
            'field_label': LabelStyle(
                font_name="Helvetica-Bold",
                font_size=8,  # Reduced from 11
                color=self.colors['secondary'],
                spacing_after=8
            ),
            'h1': LabelStyle(
                font_name="Helvetica-Bold",
                font_size=18,
                color=self.colors['accent'],
                spacing_after=35,
                alignment='center'
            ),
            'h3': LabelStyle(
                font_name="Helvetica-Bold",
                font_size=14,
                color=self.colors['accent'],
                spacing_after=25
            ),
            'h4': LabelStyle(
                font_name="Helvetica-Oblique",
                font_size=10,
                color=self.colors['secondary'],
                spacing_after=20
            ),
            'p': LabelStyle(
                font_name="Helvetica",
                font_size=10,
                color=self.colors['secondary'],
                spacing_after=30
            ),
            'regular': LabelStyle(
                font_name="Helvetica",
                font_size=9,  # Reduced from 11
                color=self.colors['secondary'],
                spacing_after=12  # Reduced from 15
            )
        }
        self.current_group = None
        self.group_fields = []
        self.group_configs = {
            '*name_details': {
                'columns': 3,
                'widths': [0.43, 0.43, 0.14],  # Proportional widths
                'spacing': 10
            },
            '*address_details': {
                'columns': 4,
                'widths': [0.50, 0.20, 0.10, 0.20],
                'spacing': 10
            },
            'contact_information': {
                'columns': 3,
                'widths': [0.33, 0.33, 0.33],
                'spacing': 10
            },
            'two_columns': {
                'columns': 2,
                'widths': [0.5, 0.5],
                'spacing': 10,
                'with_box': True,
                'box_padding': 20
            }
        }

    def _prepare_logo_image(self):
        """Prepare logo image using PIL and convert to format compatible with ReportLab"""
        try:
            if not os.path.exists(self.logo_path):
                print(f"Logo file not found: {self.logo_path}")
                return None, None

            # Open and process the image
            pil_img = Image.open(self.logo_path)
            original_size = pil_img.size
            
            # Convert RGBA to RGB if necessary
            if pil_img.mode in ('RGBA', 'LA'):
                background = Image.new('RGB', pil_img.size, (255, 255, 255))
                if pil_img.mode == 'RGBA':
                    background.paste(pil_img, mask=pil_img.split()[3])
                else:
                    background.paste(pil_img.convert('RGB'), mask=pil_img.split()[1])
                pil_img = background
            elif pil_img.mode == 'P':
                pil_img = pil_img.convert('RGB')
            
            # Convert PIL Image to ImageReader
            img_reader = ImageReader(pil_img)
            return img_reader, original_size

        except Exception as e:
            print(f"Error preparing logo image: {str(e)}")
            return None, None

    def _initialize_page(self, c):
        """Set up page with header and styling"""
        width, height = letter
        
        # Default header height in case there's no logo
        header_height = 75
        scaled_height = 75
        
        # Prepare and add logo
        img_reader, original_size = self._prepare_logo_image()
        if img_reader and original_size:
            try:
                original_width, original_height = original_size
                fixed_width = 100
                fixed_height = 75

                # Calculate scaling factor to maintain aspect ratio
                scale_factor = min(fixed_width / original_width, fixed_height / original_height)
                scaled_width = original_width * scale_factor
                scaled_height = original_height * scale_factor

                # Center the logo on the page
                c.drawImage(img_reader, 
                           (width - scaled_width) / 2, 
                           height - scaled_height - 20, 
                           width=scaled_width, 
                           height=scaled_height)
                
                header_height = scaled_height + 85 + 20
            except Exception as e:
                print(f"Error drawing logo: {str(e)}")
        
        # Set colors and fonts for header text
        c.setFillColor(self.colors['primary'])
        c.setFont("Helvetica", 8)
        
        # Draw header text
        y_offset = height - scaled_height - 40
        c.drawCentredString(width / 2, y_offset, self.business_name)
        c.drawCentredString(width / 2, y_offset - 15, self.address)
        c.drawCentredString(width / 2, y_offset - 30, self.phone)
        c.drawCentredString(width / 2, y_offset - 45, self.email)

        # Reset positioning for form fields
        self.current_y = height - header_height - 20
        c.setFont("Helvetica", 10)

    def _get_options(self, field_options):
        if isinstance(field_options, dict):
            return [(value, label) for value, label in field_options.items()]
        elif isinstance(field_options, list):
            return [(str(i), str(opt)) for i, opt in enumerate(field_options)]
        return []

    def _check_page_break(self, c, needed_height):
        if self.current_y - needed_height < self.margin_bottom:
            c.showPage()
            self._initialize_page(c)
            c.acroForm.needAppearances = True
            self.current_page += 1
            return True
        return False

    def _wrap_text(self, text, width, fontSize=10):
        return simpleSplit(text, 'Helvetica', fontSize, width)

    def generate_pdf(self, output_filename):
        # First pass - generate PDF without page numbers to get total count
        c = canvas.Canvas(output_filename, pagesize=letter)
        c.setTitle(self.data['form'].get('name', 'Generated Form'))
        c.acroForm.needAppearances = True
        
        # Initialize first page
        self._initialize_page(c)

        for field in self.data['form']['content']['form']['fields']:
            label = field.get('label', '')
            field_name = field.get('name', '')
            field_type = field.get('type', '').lower().strip()

            if field_type in ['pdf_download', 'submit']:
                continue

            # Calculate space needed
            needed_height = self._calculate_field_height(field_type, label, field.get('option', {}))
            
            # Check for page break
            self._check_page_break(c, needed_height)

            # Draw the field with modern styling
            self._draw_field(c, field_type, field_name, label, field.get('option', {}))

        # Get total page count
        total_pages = c.getPageNumber()
        c.save()

        # Second pass - regenerate PDF with correct page numbers
        c = canvas.Canvas(output_filename, pagesize=letter)
        c.setTitle(self.data['form'].get('name', 'Generated Form'))
        c.acroForm.needAppearances = True
        self.current_page = 1
        
        # Initialize first page
        self._initialize_page(c)

        for field in self.data['form']['content']['form']['fields']:
            label = field.get('label', '')
            field_name = field.get('name', '')
            field_type = field.get('type', '').lower().strip()

            if field_type in ['pdf_download', 'submit']:
                continue

            # Save current font state
            current_font = c._fontname
            current_size = c._fontsize
            current_color = c._fillColorObj  # Fixed attribute name

            # Draw page number
            c.setFont("Helvetica", 9)
            c.setFillColor(self.colors['secondary'])
            c.drawString(
                self.page_width - self.margin_x - 40,
                self.margin_bottom - 20,
                f"Page {self.current_page} of {total_pages}"
            )

            # Restore previous font state
            c.setFont(current_font, current_size)
            c.setFillColor(current_color)

            needed_height = self._calculate_field_height(field_type, label, field.get('option', {}))
            
            if self._check_page_break(c, needed_height):
                # After page break, reset to previous font state
                c.setFont(current_font, current_size)
                c.setFillColor(current_color)

            self._draw_field(c, field_type, field_name, label, field.get('option', {}))

        c.save()
        
    def _get_label_style(self, field_type, label):
        """Determine the appropriate label style based on field type and content"""
        if field_type == 'label':
            # Only debug print if we detect HTML tags
            has_html = '<h1>' in label.lower() or '<h3>' in label.lower() or '<h4>' in label.lower() or '<p>' in label.lower()
            if has_html:
                if '<h1>' in label.lower():
                    return self.label_styles['h1']
                elif '<h3>' in label.lower():
                    return self.label_styles['h3']
                elif '<h4>' in label.lower():
                    return self.label_styles['h4']
                elif '<p>' in label.lower():
                    return self.label_styles['p']
            return self.label_styles['regular']
        return self.label_styles['field_label']
    
    def _check_page_break(self, c, needed_height):
        if self.current_y - needed_height < self.margin_bottom:
            c.showPage()
            self._initialize_page(c)
            c.acroForm.needAppearances = True
            self.current_page += 1
            return True
        return False

    def _count_total_pages(self):
        """Calculate total number of pages needed"""
        temp_y = self.page_height - 72
        page_count = 1
        
        for field in self.data['form']['content']['form']['fields']:
            if field.get('type', '').lower().strip() in ['pdf_download', 'submit']:
                continue
                
            needed_height = self._calculate_field_height(
                field.get('type', '').lower().strip(),
                self._strip_html_tags(field.get('label', '')),
                field.get('option', {})
            )
            
            if temp_y - needed_height < self.margin_bottom:
                page_count += 1
                temp_y = self.page_height - 72 - needed_height
            else:
                temp_y -= needed_height
                
        return page_count

    def _draw_field(self, c, field_type, field_name, label, options):
        """Draw a form field with its label"""
        # Save the current font state
        current_font = c._fontname
        current_size = c._fontsize
        current_color = c._fillColorObj

        if label:
            style = self._get_label_style(field_type, label)
            draw_line = field_type == 'label' and ('<h1>' in label.lower())
            self._draw_label(c, label, style, draw_line)
        
        # Reset to field label style for form fields
        if field_type != 'label':
            field_label_style = self.label_styles['field_label']
            c.setFont(field_label_style.font_name, field_label_style.font_size)
            c.setFillColor(field_label_style.color)
            
            if field_type in ['text', 'email', 'date', 'select']:
                self._draw_text_field(c, field_name, label)
            elif field_type == 'textarea':
                self._draw_textarea(c, field_name, label)
            elif field_type == 'radio':
                self._draw_radio_buttons(c, field_name, options)
            elif field_type == 'checkbox':
                self._draw_checkboxes(c, field_name, options)
                
        c.setFont(current_font, current_size)
        c.setFillColor(current_color)
            
    def _draw_label(self, c, text, style, draw_line=False):
        """Unified method to draw labels with consistent styling"""
        # Save current font state
        current_font = c._fontname
        current_size = c._fontsize
        current_color = c._fillColorObj

        has_html = '<h1>' in text.lower() or '<h3>' in text.lower() or '<h4>' in text.lower() or '<p>' in text.lower()
        
        try:
            c.setFont(style.font_name, style.font_size)
            c.setFillColor(style.color)
        except Exception as e:
            print(f"Error setting font {style.font_name}: {str(e)}")
        
        clean_text = self._strip_html_tags(text)
        wrapped_lines = self._wrap_text(clean_text, self.field_width - 40)
        
        for i, line in enumerate(wrapped_lines):
            if style.alignment == 'center':
                text_width = c.stringWidth(line, style.font_name, style.font_size)
                x_position = (self.page_width - text_width) / 2
            else:
                x_position = self.margin_x
                
            c.drawString(x_position, self.current_y, line)
            if i < len(wrapped_lines) - 1:
                self.current_y -= 15
        
        if draw_line:
            # Add extra gap before drawing the line
            self.current_y -= 10
            c.setLineWidth(0.5)
            c.setStrokeColor(self.colors['border'])
            c.line(self.margin_x, self.current_y,
                self.margin_x + self.field_width, self.current_y)
        
        self.current_y -= style.spacing_after

        # Restore original font state
        c.setFont(current_font, current_size)
        c.setFillColor(current_color)
        
    def _draw_text_field(self, c, field_name, label):
        c.acroForm.textfield(
            name=field_name,
            tooltip=label,
            x=self.margin_x,
            y=self.current_y - self.field_height,
            width=self.field_width,
            height=self.field_height,
            fontSize=10,
            borderWidth=0.5,
            borderColor=self.colors['border'],
            fillColor=self.colors['background'],
            textColor=self.colors['primary'],
            fieldFlags=0
        )
        # Increase space after field from 15 to 25
        self.current_y -= (self.field_height + 25)

    def _draw_textarea(self, c, field_name, label):
        textarea_height = 100
        c.acroForm.textfield(
            name=field_name,
            tooltip=label,
            x=self.margin_x,
            y=self.current_y - textarea_height,
            width=self.field_width,
            height=textarea_height,
            fontSize=10,
            borderWidth=0.5,
            borderColor=self.colors['border'],
            fillColor=self.colors['background'],
            textColor=self.colors['primary'],
            fieldFlags=4096
        )
        self.current_y -= (textarea_height + 20)

    def _draw_radio_buttons(self, c, group_name, options):
        # Save current font state
        current_font = c._fontname
        current_size = c._fontsize
        current_color = c._fillColorObj

        options_list = self._get_options(options)
        radio_size = 7
        
        # Set to regular style for radio button labels
        c.setFont("Helvetica", 9)
        c.setFillColor(self.colors['primary'])

        for value, label in options_list:
            if self._check_page_break(c, 15):  # Reduced from 20
                continue

            c.acroForm.radio(
                name=group_name,
                value=value,
                selected=False,
                x=self.margin_x,
                y=self.current_y - radio_size,
                size=radio_size,
                buttonStyle='circle',
                borderStyle='solid',
                borderWidth=0.5,
                borderColor=self.colors['border'],
                fillColor=self.colors['background'],
                textColor=self.colors['primary'],
                forceBorder=True,
                fieldFlags=0
            )
            
            c.drawString(self.margin_x + 15, self.current_y - 6, label)
            self.current_y -= 15  # Reduced from 20 to decrease spacing between options

        # Add bottom margin after all radio buttons
        self.current_y -= 20
        
        # Restore original font state
        c.setFont(current_font, current_size)
        c.setFillColor(current_color)

    def _draw_checkboxes(self, c, group_name, options):
        # Save current font state
        current_font = c._fontname
        current_size = c._fontsize
        current_color = c._fillColorObj

        options_list = self._get_options(options)
        checkbox_size = 7

        # Set to regular style for checkbox labels
        c.setFont("Helvetica", 9)
        c.setFillColor(self.colors['primary'])

        for value, label in options_list:
            if self._check_page_break(c, 20):
                continue

            cleaned_label = self._strip_html_tags(label)
            wrapped_lines = self._wrap_text(cleaned_label, self.field_width - 20)

            c.acroForm.checkbox(
                name=f"{group_name}_{value}",
                checked=False,
                x=self.margin_x,
                y=self.current_y - checkbox_size,
                size=checkbox_size,
                buttonStyle='check',
                borderStyle='solid',
                borderWidth=0.5,
                borderColor=self.colors['border'],
                fillColor=self.colors['background'],
                textColor=self.colors['primary'],
                forceBorder=True,
                fieldFlags=0
            )
            
            current_line_y = self.current_y
            for line in wrapped_lines:
                c.drawString(self.margin_x + 15, current_line_y - 6, line)
                current_line_y -= 15
            
            self.current_y -= (len(wrapped_lines) * 15 + 10)

        # Restore original font state
        c.setFont(current_font, current_size)
        c.setFillColor(current_color)

    def _calculate_field_height(self, field_type, label, options):
        """Calculate the height needed for a field and its label"""
        height = 0
        
        # Calculate label height
        if label:
            wrapped_lines = self._wrap_text(label, self.field_width - 40)
            line_height = len(wrapped_lines) * 15
            
            if field_type == 'label':
                if '<h1>' in label:
                    height += line_height + self.label_styles['h1'].spacing_after
                elif '<h3>' in label:
                    height += line_height + self.label_styles['h3'].spacing_after
                elif '<h4>' in label:
                    height += line_height + self.label_styles['h4'].spacing_after
                elif '<p>' in label:
                    height += line_height + self.label_styles['p'].spacing_after
                else:
                    height += line_height + self.label_styles['regular'].spacing_after
            else:
                height += line_height + self.label_styles['field_label'].spacing_after
        
        # Add field height
        if field_type in ['text', 'email', 'date']:
            height += self.field_height + 25
        elif field_type == 'textarea':
            height += 120
        elif field_type in ['radio', 'checkbox']:
            options_list = self._get_options(options)
            height += len(options_list) * 20 + 5
            
        return height

    def _strip_html_tags(self, text):
        import re
        clean = re.compile('<.*?>')
        return re.sub(clean, '', text)

def generate_form_pdf(json_file_path, output_pdf_path):
    with open(json_file_path, 'r') as file:
        form_data = json.load(file)

    generator = ModernPDFFormGenerator(form_data)
    generator.generate_pdf(output_pdf_path)

if __name__ == "__main__":
    json_path = '/Users/camerondyas/Documents/scripts/pythonScripts/JSONToPDF/form/form.json'
    output_path = '/Users/camerondyas/Documents/scripts/pythonScripts/JSONToPDF/form/generated_form.pdf'
    generate_form_pdf(json_path, output_path)