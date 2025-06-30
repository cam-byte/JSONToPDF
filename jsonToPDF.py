import os
from dotenv import load_dotenv
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
import json

# Load environment variables from .env file
load_dotenv()

from constants import (
    MARGINS, 
    FIELD_DIMENSIONS, 
    BUSINESS_INFO, 
    COLORS,
    GROUP_CONFIGS,
    FULL_WIDTH_FIELDS 
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
        
        # REMOVED: Font registration - using standard fonts instead
        # Standard fonts like 'Helvetica', 'Helvetica-Bold' are always available
        
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

        # Get the first key and parse form data
        self.form_key = self._get_first_form_key()
        self.form_data = self._find_form_data()
        
    def _setup_canvas_for_acrobat(self, c):
        """CRITICAL: Set up canvas for Adobe Acrobat compatibility"""
        # Use only standard PDF fonts that don't need registration
        c.setFont('Helvetica', 12)  # Standard font, always available
        c.setFillColorRGB(0, 0, 0)  # Explicit black text
        c.setStrokeColorRGB(0, 0, 0)  # Explicit black stroke

    def _get_first_form_key(self):
        """Get the first key from the JSON data (the main form identifier)"""
        if isinstance(self.data, dict) and self.data:
            first_key = list(self.data.keys())[0]
            return first_key
        return None

    def _find_form_data(self):
        """Find the actual form data structure in the JSON"""
        if not self.form_key:
            return self.data
            
        # Navigate through the structure: first_key -> content -> nested_form_key -> fields
        try:
            main_section = self.data[self.form_key]
            if 'content' in main_section:
                content = main_section['content']
                # Look for the nested form key (usually similar to main key but different)
                for key, value in content.items():
                    if isinstance(value, dict) and 'fields' in value:
                        return value
                        
            # Fallback: search recursively
            def search_for_fields(obj, path=""):
                if isinstance(obj, dict):
                    if 'fields' in obj:
                        return obj, path
                    for key, value in obj.items():
                        result, result_path = search_for_fields(value, f"{path}.{key}" if path else key)
                        if result:
                            return result, result_path
                elif isinstance(obj, list):
                    for i, item in enumerate(obj):
                        result, result_path = search_for_fields(item, f"{path}[{i}]" if path else f"[{i}]")
                        if result:
                            return result, result_path
                return None, ""

            form_data, path = search_for_fields(self.data)
            if form_data:
                print(f"Found form data at: {path}")
                return form_data
            else:
                print("No 'fields' key found, using entire JSON as form data")
                return self.data
                
        except KeyError as e:
            print(f"Key error when parsing form data: {e}")
            return self.data

    def _get_form_title(self):
        """Extract form title from various possible locations"""
        # Try common title field names
        title_fields = ['form_name', 'title', 'name', 'form_title']
        
        # First check the form_data itself
        for field in title_fields:
            if field in self.form_data:
                return self.form_data[field]
        
        # Then check the root data
        for field in title_fields:
            if field in self.data:
                return self.data[field]
        
        # Try to find it in nested structures
        def find_title(obj):
            if isinstance(obj, dict):
                for field in title_fields:
                    if field in obj and isinstance(obj[field], str):
                        return obj[field]
                for value in obj.values():
                    result = find_title(value)
                    if result:
                        return result
            return None
        
        title = find_title(self.data)
        return title if title else "Generated Form"

    def _get_fields(self):
        """Extract fields from the form data"""
        if 'fields' in self.form_data:
            return self.form_data['fields']
        elif isinstance(self.form_data, list):
            return self.form_data
        else:
            print("Warning: No fields found in form data")
            return []

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

    # In your ModernPDFFormGenerator class, update the _process_fields method:

    def _process_fields(self, c, total_pages=None):
        fields = self._get_fields()
        num_fields = len(fields)
        
        i = 0
        while i < num_fields:
            field = fields[i]
            
            label = field.get('label', '')
            field_name = field.get('name', '')
            field_type = field.get('type', '').lower().strip()

            prev_field_type = fields[i-1].get('type', '').lower().strip() if i > 0 else None
            next_field_type = fields[i+1].get('type', '').lower().strip() if i+1 < num_fields else None

            # Skip submission fields
            if field_type in ['pdf_download', 'submit']:
                i += 1
                continue

            # --- DYNAMIC LOGIC: Force new row for specific fields or radio between text fields ---
            # Check for Women Only label by content
            is_women_only_label = (field_type == 'label' and 
                                'women only' in label.lower() and 
                                'are you' in label.lower())
            
            if (field_name in FULL_WIDTH_FIELDS or 
                is_women_only_label or
                (field_type == 'radio' and 
                (prev_field_type == 'text' or next_field_type == 'text') and 
                self.current_group is None)):
                
                # Temporarily end current group if any
                temp_group = self.current_group
                if self.current_group:
                    group_field = GroupField(self, c)
                    group_field.end_group()
                    self.current_group = None
                
                # Draw the field as full-width
                self._draw_field(c, field_type, field_name, label, field.get('option', {}))
                i += 1
                
                # Restore the group if we temporarily ended it
                if temp_group:
                    group_field = GroupField(self, c)
                    group_field.start_group(temp_group)
                
                continue

            # Calculate needed height with reasonable estimates
            needed_height = _calculate_field_height(
                field_type, label, field.get('option', {}), 
                self.field_width, self.field_height, 
                self.label_styles
            )

            if _check_page_break(self, c, needed_height):
                # CRITICAL: Increment page counter BEFORE initializing new page
                self.current_page += 1
                
                self.page_manager.initialize_page(c)
                if self.current_group:
                    self.group_fields = []
                    self.group_start_y = self.current_y

            # Draw the field
            self._draw_field(c, field_type, field_name, label, field.get('option', {}))
            i += 1

    def generate_pdf(self, output_filename):
        """Updated with minimal Adobe Acrobat compatibility fixes"""
        # First pass to count pages
        c = canvas.Canvas(
            output_filename, 
            pagesize=letter,
            pageCompression=0,  # Better Adobe compatibility
            encoding='WinAnsiEncoding'  # Most compatible encoding
        )
        
        form_title = self._get_form_title()
        c.setTitle(form_title)
        c.acroForm.needAppearances = True
        c.acroForm.sigFlags = 0
        
        # CRITICAL: Set up for Adobe compatibility
        self._setup_canvas_for_acrobat(c)
        
        self.page_manager.initialize_page(c)
        self._process_fields(c)
        total_pages = c.getPageNumber()
        c.save()

        # Second pass with page numbers - reset state
        self.current_page = 1
        self.current_y = self.page_height - self.margin_x
        self.current_group = None
        self.group_fields = []
        
        c = canvas.Canvas(
            output_filename, 
            pagesize=letter,
            pageCompression=0,  # Better Adobe compatibility
            encoding='WinAnsiEncoding'  # Most compatible encoding
        )
        c.setTitle(form_title)
        c.acroForm.needAppearances = True
        c.acroForm.sigFlags = 0
        
        # CRITICAL: Set up for Adobe compatibility again
        self._setup_canvas_for_acrobat(c)
        
        self.page_manager.initialize_page(c)
        self._process_fields(c, total_pages)
        c.save()
        
    def _fix_pdf_for_acrobat_minimal(self, pdf_path):
        """Minimal PDF fix that doesn't interfere with radio buttons"""
        try:
            from PyPDF2 import PdfReader, PdfWriter
            from PyPDF2.generic import BooleanObject, NameObject
            
            reader = PdfReader(pdf_path)
            writer = PdfWriter()
            
            # ONLY add NeedAppearances flag, don't modify anything else
            for page_num, page in enumerate(reader.pages):
                writer.add_page(page)
            
            # Add ONLY the NeedAppearances flag to the catalog
            if hasattr(writer, '_root_object') and writer._root_object:
                if "/AcroForm" not in writer._root_object:
                    writer._root_object[NameObject("/AcroForm")] = {}
                writer._root_object[NameObject("/AcroForm")][NameObject("/NeedAppearances")] = BooleanObject(True)
            
            # Write back
            with open(pdf_path, "wb") as output_file:
                writer.write(output_file)
                
            
        except Exception as e:
            print(f"Minimal PDF processing failed: {e}")
        
    def generate_pdf_no_postprocessing(self, output_filename):
        """Generate PDF without any post-processing that might break radio buttons"""
        # Single pass - no post-processing
        c = canvas.Canvas(
            output_filename, 
            pagesize=letter,
            pageCompression=0,
            encoding='WinAnsiEncoding'
        )
        
        form_title = self._get_form_title()
        c.setTitle(form_title)
        
        # Set needAppearances directly in ReportLab
        c.acroForm.needAppearances = True
        c.acroForm.sigFlags = 0
        
        self._setup_canvas_for_acrobat(c)
        self.page_manager.initialize_page(c)
        self._process_fields(c)
        c.save()
        


# FIXED: Functions moved outside the class (correct indentation)
def generate_form_pdf(json_file_path, output_pdf_path):
    """Generate form PDF from JSON file"""
    if not os.path.exists(json_file_path):
        raise FileNotFoundError(f"JSON file not found: {json_file_path}")
    
    with open(json_file_path, 'r', encoding='utf-8') as file:
        form_data = json.load(file)

    generator = ModernPDFFormGenerator(form_data)
    generator.generate_pdf(output_pdf_path)


if __name__ == "__main__":
    # Get paths from environment variables with fallback defaults
    json_path = os.getenv('JSON_INPUT_PATH', 
                         '/Users/camerondyas/Documents/scripts/pythonScripts/JSONToPDF/form/form.json')
    output_path = os.getenv('PDF_OUTPUT_PATH', 
                           '/Users/camerondyas/Documents/scripts/pythonScripts/JSONToPDF/form/generated_form.pdf')
    
    print(f"Using JSON input path: {json_path}")
    print(f"Using PDF output path: {output_path}")
    
    try:
        if os.path.exists(output_path):
            # Delete the file
            os.remove(output_path)
            print(f"Deleted existing file: {output_path}")
        generate_form_pdf(json_path, output_path)
        print(f"PDF generated successfully: {output_path}")
    except FileNotFoundError as e:
        print(f"File error: {e}")
    except json.JSONDecodeError as e:
        print(f"JSON parsing error: {e}")
    except KeyError as e:
        print(f"Missing required data in JSON: {e}")
    except Exception as e:
        print(f"Error generating PDF: {e}")
        import traceback
        traceback.print_exc()