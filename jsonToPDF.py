# jsonToPDF.py
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
from utils import _calculate_field_height, _check_page_break

class ModernPDFFormGenerator:
    def __init__(self, json_data):
        self.data = json_data
        self.page_width, self.page_height = letter
        
        pdfmetrics.registerFont(pdfmetrics.Font('Helvetica', 'Helvetica', 'WinAnsiEncoding'))
        pdfmetrics.registerFont(pdfmetrics.Font('Helvetica-Bold', 'Helvetica-Bold', 'WinAnsiEncoding'))
        pdfmetrics.registerFont(pdfmetrics.Font('Helvetica-Oblique', 'Helvetica-Oblique', 'WinAnsiEncoding'))
        pdfmetrics.registerFont(pdfmetrics.Font('Helvetica-BoldOblique', 'Helvetica-BoldOblique', 'WinAnsiEncoding'))
        
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
        
        self.current_group = None
        self.group_fields = []
        self.group_configs = GROUP_CONFIGS

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

        # Calculate field position based on group
        field_x = self.margin_x
        field_width = self.field_width
        
        if self.current_group and self.group_fields:
            config = self.group_configs.get(self.current_group, {})
            column_index = len(self.group_fields) % config.get('columns', 1)
            if column_index > 0:
                field_x = self.margin_x + sum(self.column_widths[:column_index]) + (config.get('spacing', 10) * column_index)
                self.current_y = self.group_fields[-1]['y']
            
            field_width = self.column_widths[column_index]

        # Draw label first
        if field_type == 'label':
            style = self.label_manager.get_label_style(field_type, label)
            draw_line = '<h1>' in label.lower()
            self.label_manager.draw_label(c, label, style, draw_line)
        elif field_type == 'radio' and label:
            field_label_style = self.label_styles['field_label']
            c.setFont(field_label_style.font_name, field_label_style.font_size)
            c.setFillColor(field_label_style.color)
            c.drawString(field_x, self.current_y + 10, label)
        elif label:  # For non-label field types
            field_label_style = self.label_styles['field_label']
            c.setFont(field_label_style.font_name, field_label_style.font_size)
            c.setFillColor(field_label_style.color)
            c.drawString(field_x, self.current_y + 5, label)
        
        # Store field info for group positioning before drawing the field
        if self.current_group is not None:
            self.group_fields.append({
            'name': field_name,
            'x': field_x,
            'y': self.current_y,
            'width': field_width
        })
    
        # Draw the field if it's not a label type
        if field_type != 'label':
            if field_type in ['text', 'email', 'date', 'select']:
                text_field = TextField(self, c)
                text_field.draw(field_name, label)
            elif field_type == 'textarea':
                text_area = TextArea(self, c)
                text_area.draw(field_name, label)
            elif field_type == 'radio':
                radio_button = RadioButton(self, c)
                radio_button.draw(field_name, label, options)
            elif field_type == 'checkbox':
                check_box = CheckBox(self, c)
                check_box.draw(field_name, label, options)
                    
        c.setFont(current_font, current_size)
        c.setFillColor(current_color)

    def _process_fields(self, c, total_pages=None):
        for field in self.data['form']['content']['form']['fields']:
            label = field.get('label', '')
            field_name = field.get('name', '')
            field_type = field.get('type', '').lower().strip()

            if field_type in ['pdf_download', 'submit']:
                continue

            if total_pages:
                self.page_manager.draw_page_number(c, self.current_page, total_pages)

            needed_height = _calculate_field_height(
                field_type, label, field.get('option', {}), 
                self.field_width, self.field_height, 
                self.label_styles
            )
            
            if _check_page_break(self, c, needed_height):
                self.page_manager.initialize_page(c)

            self._draw_field(c, field_type, field_name, label, field.get('option', {}))

    def generate_pdf(self, output_filename):
        c = canvas.Canvas(output_filename, pagesize=letter)
        c.setTitle(self.data['form'].get('name', 'Generated Form'))
        c.acroForm.needAppearances = True
        
        self.page_manager.initialize_page(c)
        self._process_fields(c)
        total_pages = c.getPageNumber()
        c.save()

        c = canvas.Canvas(output_filename, pagesize=letter)
        c.setTitle(self.data['form'].get('name', 'Generated Form'))
        c.acroForm.needAppearances = True
        self.current_page = 1
        
        self.page_manager.initialize_page(c)
        self._process_fields(c, total_pages)
        c.save()

def generate_form_pdf(json_file_path, output_pdf_path):
    with open(json_file_path, 'r') as file:
        form_data = json.load(file)

    generator = ModernPDFFormGenerator(form_data)
    generator.generate_pdf(output_pdf_path)

if __name__ == "__main__":
    json_path = '/Users/camerondyas/Documents/scripts/pythonScripts/JSONToPDF/form/form.json'
    output_path = '/Users/camerondyas/Documents/scripts/pythonScripts/JSONToPDF/form/generated_form.pdf'
    generate_form_pdf(json_path, output_path)