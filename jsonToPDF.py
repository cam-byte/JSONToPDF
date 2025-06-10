# jsonToPDF.py - CLEAN, READABLE LAYOUT (NO PAGE COUNT OPTIMIZATION)
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
import json

from constants import (
    MARGINS, 
    FIELD_DIMENSIONS, 
    BUSINESS_INFO, 
    COLORS,
    GROUP_CONFIGS
)
from label_styles import LABEL_STYLES
from page_manager import PageManager
from label_manager import LabelManager
from fields.text_field import TextField
from fields.text_area import TextArea
from fields.check_box import CheckBox
from fields.radio_button import RadioButton
from fields.group_field import GroupField
from fields.select_field import SelectField
from utils import _calculate_field_height, _check_page_break

class ModernPDFFormGenerator:
    def __init__(self, json_data):
        self.data = json_data
        self.page_width, self.page_height = letter
        
        # Register fonts
        pdfmetrics.registerFont(pdfmetrics.Font('Helvetica', 'Helvetica', 'WinAnsiEncoding'))
        pdfmetrics.registerFont(pdfmetrics.Font('Helvetica-Bold', 'Helvetica-Bold', 'WinAnsiEncoding'))
        pdfmetrics.registerFont(pdfmetrics.Font('Helvetica-Oblique', 'Helvetica-Oblique', 'WinAnsiEncoding'))
        pdfmetrics.registerFont(pdfmetrics.Font('Helvetica-BoldOblique', 'Helvetica-BoldOblique', 'WinAnsiEncoding'))
        
        # Clean, reasonable settings
        self.margin_x = MARGINS['x']
        self.margin_bottom = MARGINS['bottom']
        self.current_y = self.page_height - MARGINS['x']
        self.field_width = FIELD_DIMENSIONS['width']
        self.field_height = FIELD_DIMENSIONS['height']
        self.current_page = 1
        
        self.logo_path = BUSINESS_INFO['logo_path']
        self.address = BUSINESS_INFO['address']
        self.phone = BUSINESS_INFO['phone']
        self.email = BUSINESS_INFO['email']
        self.business_name = BUSINESS_INFO['business_name']
        
        self.colors = COLORS
        self.label_styles = LABEL_STYLES
        
        # Group handling
        self.current_group = None
        self.group_fields = []
        self.group_configs = GROUP_CONFIGS
        self.column_widths = None
        self.group_spacing = None
        self.group_columns = None
        self.group_start_y = None

        self.page_manager = PageManager(self)
        self.label_manager = LabelManager(self)

    def _draw_field(self, c, field_type, field_name, label, options):
        current_font = c._fontname
        current_size = c._fontsize
        current_color = c._fillColorObj

        if field_type == 'group_start':
            group_field = GroupField(self, c)
            group_field.start_group(field_name)
            return
        elif field_type == 'group_end':
            group_field = GroupField(self, c)
            group_field.end_group()
            return

        # Handle label-only fields
        if field_type == 'label':
            style = self.label_manager.get_label_style(field_type, label)
            draw_line = '<h1>' in label.lower()
            self.label_manager.draw_label(c, label, style, draw_line)
        else:
            # Handle form fields
            try:
                if field_type in ['text', 'email', 'date']:
                    text_field = TextField(self, c)
                    text_field.draw(field_name, label)
                elif field_type == 'select':
                    select_field = SelectField(self, c)
                    select_field.draw(field_name, label, options)
                elif field_type == 'textarea':
                    text_area = TextArea(self, c)
                    text_area.draw(field_name, label)
                elif field_type == 'radio':
                    radio_button = RadioButton(self, c)
                    radio_button.draw(field_name, label, options)
                elif field_type == 'checkbox':
                    check_box = CheckBox(self, c)
                    check_box.draw(field_name, label, options)
                else:
                    # Fallback for unknown field types
                    text_field = TextField(self, c)
                    text_field.draw(field_name, label)
            except Exception as e:
                print(f"Error drawing field '{field_name}' of type '{field_type}': {e}")
                # Fallback to text field
                text_field = TextField(self, c)
                text_field.draw(field_name, f"{label} (Error: treated as text)")
                    
        c.setFont(current_font, current_size)
        c.setFillColor(current_color)
    
    def _process_fields(self, c, total_pages=None):
        for field in self.data['dental_patient_intake_v2']['content']['dental_patient_intake_v2']['fields']:
            label = field.get('label', '')
            field_name = field.get('name', '')
            field_type = field.get('type', '').lower().strip()

            # Skip submission fields
            if field_type in ['pdf_download', 'submit']:
                continue

            # Calculate needed height with reasonable estimates
            needed_height = _calculate_field_height(
                field_type, label, field.get('option', {}), 
                self.field_width, self.field_height, 
                self.label_styles
            )
            
            # Check for page break with reasonable logic
            if _check_page_break(self, c, needed_height):
                self.page_manager.initialize_page(c)
                if total_pages:
                    self.page_manager.draw_page_number(c, self.current_page, total_pages)

            # Draw the field
            self._draw_field(c, field_type, field_name, label, field.get('option', {}))

    def generate_pdf(self, output_filename):
        # First pass to count pages
        c = canvas.Canvas(output_filename, pagesize=letter)
        c.setTitle(self.data['dental_patient_intake_v2'].get('form_name', 'Generated Form'))
        c.acroForm.needAppearances = True
        
        self.page_manager.initialize_page(c)
        self._process_fields(c)
        total_pages = c.getPageNumber()
        c.save()

        # Second pass with page numbers - reset state
        self.current_page = 1
        self.current_y = self.page_height - self.margin_x
        self.current_group = None
        self.group_fields = []
        
        c = canvas.Canvas(output_filename, pagesize=letter)
        c.setTitle(self.data['dental_patient_intake_v2'].get('form_name', 'Generated Form'))
        c.acroForm.needAppearances = True
        
        self.page_manager.initialize_page(c)
        self._process_fields(c, total_pages)
        c.save()
        
        print(f"PDF generated with {total_pages} pages")

def generate_form_pdf(json_file_path, output_pdf_path):
    with open(json_file_path, 'r') as file:
        form_data = json.load(file)

    generator = ModernPDFFormGenerator(form_data)
    generator.generate_pdf(output_pdf_path)

if __name__ == "__main__":
    json_path = '/Users/camerondyas/Documents/scripts/pythonScripts/JSONToPDF/form/form.json'
    output_path = '/Users/camerondyas/Documents/scripts/pythonScripts/JSONToPDF/form/generated_form.pdf'
    
    try:
        generate_form_pdf(json_path, output_path)
        print(f"PDF generated successfully: {output_path}")
    except Exception as e:
        print(f"Error generating PDF: {e}")
        import traceback
        traceback.print_exc()