# utils.py
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.utils import simpleSplit, ImageReader
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

def _prepare_logo_image(logo_path):
    """Prepare logo image using PIL and convert to format compatible with ReportLab"""
    try:
        if not os.path.exists(logo_path):
            print(f"Logo file not found: {logo_path}")
            return None, None

        # Open and process the image
        pil_img = Image.open(logo_path)
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

def _get_options(field_options):
    if isinstance(field_options, dict):
        return [(value, label) for value, label in field_options.items()]
    elif isinstance(field_options, list):
        return [(str(i), str(opt)) for i, opt in enumerate(field_options)]
    return []

def _wrap_text(text, width, fontSize=10):
    return simpleSplit(text, 'Helvetica', fontSize, width)

def _strip_html_tags(text):
    clean = re.compile('<.*?>')
    return re.sub(clean, '', text)
    
def _calculate_field_height(field_type, label, options, width, height, label_styles):
        """Calculate the height needed for a field and its label"""
        height = 0
        
        # Calculate label height
        if label:
            wrapped_lines = _wrap_text(label, width - 40)
            line_height = len(wrapped_lines) * 15
            
            if field_type == 'label':
                if '<h1>' in label:
                    height += line_height + label_styles['h1'].spacing_after
                elif '<h3>' in label:
                    height += line_height + label_styles['h3'].spacing_after
                elif '<h4>' in label:
                    height += line_height + label_styles['h4'].spacing_after
                elif '<p>' in label:
                    height += line_height + label_styles['p'].spacing_after
                else:
                    height += line_height + label_styles['regular'].spacing_after
            else:
                height += line_height + label_styles['field_label'].spacing_after
        
        # Add field height
        if field_type in ['text', 'email', 'date']:
            height += height + 25
        elif field_type == 'textarea':
            height += 120
        elif field_type in ['radio', 'checkbox']:
            options_list = _get_options(options)
            height += len(options_list) * 20 + 5
            
        return height

def _count_total_pages(data, margin_bottom, page_height, calculate_field_height_func):
    """Calculate total number of pages needed"""
    temp_y = page_height - 72
    page_count = 1

    for field in data['form']['content']['form']['fields']:
        if field.get('type', '').lower().strip() in ['pdf_download', 'submit']:
            continue

        needed_height = calculate_field_height_func(
            field.get('type', '').lower().strip(),
            field.get('label', ''),  # No need to strip HTML here
            field.get('option', {})
        )

        if temp_y - needed_height < margin_bottom:
            page_count += 1
            temp_y = page_height - 72 - needed_height
        else:
            temp_y -= needed_height

    return page_count

def _check_page_break(generator, canvas, needed_height):
    if generator.current_y - needed_height < generator.margin_bottom:
        canvas.showPage()
        generator.page_manager.initialize_page(canvas)
        canvas.acroForm.needAppearances = True
        generator.current_page += 1
        return True
    return False