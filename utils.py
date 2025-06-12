# utils.py - COMPLETE VERSION with all functions

import re
import os
from reportlab.lib import colors
from reportlab.lib.utils import ImageReader

def _strip_html_tags(text):
    """Remove HTML tags from text"""
    if not text:
        return ""
    clean = re.compile('<.*?>')
    return re.sub(clean, '', text)

def _get_options(option_data):
    """Extract options from various formats"""
    if not option_data:
        return []
    
    if isinstance(option_data, dict):
        return [(key, value) for key, value in option_data.items()]
    elif isinstance(option_data, list):
        return [(str(i), str(item)) for i, item in enumerate(option_data)]
    else:
        return []

def _check_page_break(generator, canvas, needed_height):
    """Check if a new page is needed"""
    if generator.current_y - needed_height < generator.margin_bottom:
        canvas.showPage()
        generator.current_page += 1
        generator.current_y = generator.page_height - generator.margin_x
        return True
    return False

def _calculate_field_height(field_type, label, options, field_width, field_height, label_styles):
    """Calculate approximate height needed for a field"""
    base_height = 40
    
    if field_type == 'textarea':
        base_height = 80
    elif field_type in ['radio', 'checkbox']:
        option_count = len(_get_options(options)) if options else 2
        base_height = 20 + (option_count * 18)
    elif field_type == 'label':
        if '<h1>' in str(label).lower():
            base_height = 25
        elif '<h3>' in str(label).lower():
            base_height = 20
        else:
            base_height = 15
    
    return base_height

def _prepare_logo_image(logo_path):
    """Prepare logo image for PDF inclusion"""
    if not logo_path or not os.path.exists(logo_path):
        return None
    
    try:
        # For reportlab, we can use ImageReader directly
        return ImageReader(logo_path)
    except Exception as e:
        print(f"Error preparing logo image: {e}")
        return None

def _calculate_logo_dimensions(logo_path, max_width=150, max_height=50):
    """Calculate appropriate logo dimensions for PDF"""
    if not logo_path or not os.path.exists(logo_path):
        return 0, 0
    
    try:
        from PIL import Image
        with Image.open(logo_path) as img:
            width, height = img.size
            
            # Calculate scaling to fit within max dimensions
            width_ratio = max_width / width if width > 0 else 1
            height_ratio = max_height / height if height > 0 else 1
            scale_ratio = min(width_ratio, height_ratio, 1)  # Don't scale up
            
            return int(width * scale_ratio), int(height * scale_ratio)
    except ImportError:
        # PIL not available, use default dimensions
        return max_width, max_height
    except Exception as e:
        print(f"Error calculating logo dimensions: {e}")
        return max_width, max_height

def wrap_text(canvas, text, max_width, font_name="Helvetica", font_size=10):
    """
    Wrap text to fit within specified width
    Returns list of lines and total height needed
    """
    if not text:
        return [], 0
    
    canvas.setFont(font_name, font_size)
    words = text.split()
    lines = []
    current_line = ""
    
    for word in words:
        # Test if adding this word would exceed max width
        test_line = current_line + (" " if current_line else "") + word
        text_width = canvas.stringWidth(test_line, font_name, font_size)
        
        if text_width <= max_width:
            current_line = test_line
        else:
            # If current line has content, save it and start new line
            if current_line:
                lines.append(current_line)
                current_line = word
            else:
                # Single word is too long, force it on the line
                lines.append(word)
                current_line = ""
    
    # Add the last line if it has content
    if current_line:
        lines.append(current_line)
    
    # Calculate total height (font_size + small spacing between lines)
    line_height = font_size + 2
    total_height = len(lines) * line_height if lines else 0
    
    return lines, total_height

def draw_wrapped_text(canvas, text, x, y, max_width, font_name="Helvetica", font_size=10, color=None):
    """
    Draw wrapped text starting at x, y position
    Returns the final Y position after drawing all lines
    """
    if not text:
        return y
    
    # Save current state
    current_font = canvas._fontname
    current_size = canvas._fontsize
    current_color = canvas._fillColorObj
    
    # Set font and color
    canvas.setFont(font_name, font_size)
    if color:
        canvas.setFillColor(color)
    
    # Get wrapped lines
    lines, total_height = wrap_text(canvas, text, max_width, font_name, font_size)
    
    # Draw each line
    line_height = font_size + 2
    current_y = y
    
    for line in lines:
        canvas.drawString(x, current_y, line)
        current_y -= line_height
    
    # Restore previous state
    canvas.setFont(current_font, current_size)
    canvas.setFillColor(current_color)
    
    return current_y

def calculate_wrapped_text_height(canvas, text, max_width, font_name="Helvetica", font_size=10):
    """
    Calculate the height needed for wrapped text without drawing it
    """
    if not text:
        return 0
    
    lines, total_height = wrap_text(canvas, text, max_width, font_name, font_size)
    return total_height

def debug_group_positioning(generator, field_name, label):
    """Debug function to print group positioning info"""
    if generator.current_group:
        group_index = len(generator.group_fields)
        column_index = group_index % generator.group_columns
        print(f"DEBUG: Field '{field_name}' (label: '{label[:30]}...' if label else 'No label')")
        print(f"  Group: {generator.current_group}")
        print(f"  Group index: {group_index}, Column: {column_index}")
        print(f"  Column widths: {generator.column_widths}")
        print(f"  Available width for column {column_index}: {generator.column_widths[column_index] if generator.column_widths else 'None'}")
        print(f"  Group spacing: {generator.group_spacing}")
        print("---")

def get_effective_field_width(generator):
    """Get the effective width for text wrapping based on current context"""
    if generator.current_group is not None and generator.column_widths:
        group_index = len(generator.group_fields)
        column_index = group_index % generator.group_columns
        effective_width = generator.column_widths[column_index]
        print(f"DEBUG: Using column width: {effective_width} for column {column_index}")
        return effective_width
    else:
        print(f"DEBUG: Using full field width: {generator.field_width}")
        return generator.field_width

# Legacy function names for compatibility
def _wrap_text(text, max_width, font_size=10):
    """Legacy wrapper for wrap_text - simplified version for label manager"""
    if not text:
        return []
    
    words = text.split()
    lines = []
    current_line = ""
    # Rough character estimate - not precise but works for basic wrapping
    chars_per_line = max(1, int(max_width / (font_size * 0.6)))
    
    for word in words:
        test_line = current_line + (" " if current_line else "") + word
        if len(test_line) <= chars_per_line:
            current_line = test_line
        else:
            if current_line:
                lines.append(current_line)
            current_line = word
    
    if current_line:
        lines.append(current_line)
    
    return lines

# Additional utility functions that might be used elsewhere
def format_phone_number(phone):
    """Format phone number for display"""
    if not phone:
        return ""
    
    # Remove all non-digit characters
    digits = re.sub(r'\D', '', phone)
    
    # Format as (XXX) XXX-XXXX if 10 digits
    if len(digits) == 10:
        return f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"
    elif len(digits) == 11 and digits[0] == '1':
        return f"({digits[1:4]}) {digits[4:7]}-{digits[7:]}"
    else:
        return phone  # Return original if can't format

def validate_email(email):
    """Basic email validation"""
    if not email:
        return False
    
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def sanitize_field_name(name):
    """Sanitize field name for PDF form fields"""
    if not name:
        return "field"
    
    # Replace invalid characters with underscores
    sanitized = re.sub(r'[^a-zA-Z0-9_]', '_', name)
    
    # Ensure it doesn't start with a number
    if sanitized and sanitized[0].isdigit():
        sanitized = "field_" + sanitized
    
    return sanitized or "field"

def convert_to_points(value, unit='pt'):
    """Convert various units to points"""
    if unit == 'pt':
        return value
    elif unit == 'in':
        return value * 72
    elif unit == 'cm':
        return value * 28.35
    elif unit == 'mm':
        return value * 2.835
    else:
        return value  # Assume points if unknown