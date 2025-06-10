# utils.py - CLEAN IMPLEMENTATION WITH REASONABLE CALCULATIONS
import re
from PIL import Image
from reportlab.lib.utils import ImageReader
from collections import namedtuple

LabelStyle = namedtuple('LabelStyle', ['font_name', 'font_size', 'color', 'spacing_after', 'alignment'])

def _strip_html_tags(text):
    """Remove HTML tags from text"""
    clean = re.compile('<.*?>')
    return re.sub(clean, '', text)

def _wrap_text(text, max_width, font_size):
    """Simple text wrapping with reasonable accuracy"""
    if not text:
        return []
    
    # Better character width calculation
    char_width = font_size * 0.6
    max_chars = int(max_width / char_width) if char_width > 0 else 60
    
    words = text.split()
    lines = []
    current_line = ""
    
    for word in words:
        test_line = current_line + " " + word if current_line else word
        if len(test_line) <= max_chars:
            current_line = test_line
        else:
            if current_line:
                lines.append(current_line)
            current_line = word
    
    if current_line:
        lines.append(current_line)
    
    return lines if lines else [""]

def _get_options(options_data):
    """Extract options from various data formats"""
    if not options_data:
        return []
    
    if isinstance(options_data, list):
        return [(str(opt), str(opt)) for opt in options_data]
    
    if isinstance(options_data, dict):
        if 'options' in options_data:
            opts = options_data['options']
            if isinstance(opts, list):
                return [(str(opt), str(opt)) for opt in opts]
            elif isinstance(opts, dict):
                return list(opts.items())
        
        # Handle direct key-value pairs
        return list(options_data.items())
    
    return []

def _prepare_logo_image(logo_path):
    """Prepare logo image for ReportLab"""
    try:
        with Image.open(logo_path) as img:
            if img.mode != 'RGB':
                img = img.convert('RGB')
            return ImageReader(img), img.size
    except Exception as e:
        print(f"Logo error: {e}")
        return None, None

def _calculate_field_height(field_type, label, options, field_width, field_height, label_styles):
    """Calculate needed height for a field with reasonable estimates"""
    if field_type == 'group_start' or field_type == 'group_end':
        return 0
    
    # Reasonable base heights that account for labels and spacing
    heights = {
        'label': 20,      # For standalone labels
        'text': 35,       # Label + field + spacing
        'email': 35,      # Label + field + spacing
        'date': 35,       # Label + field + spacing
        'select': 35,     # Label + field + spacing
        'textarea': 70,   # Label + larger field + spacing
        'radio': 35,      # Base for radio buttons
        'checkbox': 35    # Base for checkboxes
    }
    
    base_height = heights.get(field_type, 35)
    
    # Adjust for radio buttons with multiple options
    if field_type == 'radio':
        options_list = _get_options(options)
        if len(options_list) > 3:  # Vertical layout needed
            base_height += (len(options_list) - 3) * 18
    
    # Adjust for checkboxes with multiple options
    if field_type == 'checkbox':
        options_list = _get_options(options)
        if len(options_list) > 1:
            base_height += (len(options_list) - 1) * 18
    
    return base_height

def _check_page_break(generator, canvas, needed_height):
    """Check if page break is needed with reasonable logic"""
    # Leave reasonable margin at bottom
    bottom_threshold = generator.margin_bottom + 50
    available_space = generator.current_y - bottom_threshold
    
    # Only break page if we really need to
    if available_space < needed_height:
        canvas.showPage()
        generator.current_page += 1
        return True
    return False