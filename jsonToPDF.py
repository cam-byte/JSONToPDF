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
    FULL_WIDTH_FIELDS,
    AUTO_FLOW_FIELD_TYPES,
    FLOW_BREAK_FIELD_TYPES,
    AUTO_FLOW_CONFIG
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
    def __init__(self, json_data, business_info=None):
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

        # Use provided business_info or fall back to defaults from constants
        biz = business_info or BUSINESS_INFO
        self.logo_path = biz.get('logo_path') or BUSINESS_INFO.get('logo_path')
        self.address = biz.get('address') or BUSINESS_INFO.get('address', '')
        self.phone = biz.get('phone') or BUSINESS_INFO.get('phone', '')
        self.email = biz.get('email') or BUSINESS_INFO.get('email', '')
        self.business_name = biz.get('business_name') or BUSINESS_INFO.get('business_name', '')
        
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
        self.group_stack = []

        self.page_manager = PageManager(self)
        self.label_manager = LabelManager(self)

        # Inline container state (for fill-in-the-blank paragraphs)
        self.inline_state = None

        # Auto-flow state (CSS flexbox-like 2-column layout for text fields)
        self.auto_flow_active = False
        self.auto_flow_field_count = 0

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
            from fields.group_field import GroupField
            group_field = GroupField(self, c)
            group_field.start_group(field_name)
            return
        elif field_type == 'group_end':
            from fields.group_field import GroupField
            group_field = GroupField(self, c)
            group_field.end_group()
            return

        # Handle inline_text fields (for fill-in-the-blank paragraphs)
        if field_type == 'inline_text':
            from fields.inline_text_field import InlineTextField
            inline_field = InlineTextField(self, c)
            inline_field.draw_text(label)
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
                    # Check if we're inside an inline container
                    if hasattr(self, 'inline_state') and self.inline_state is not None:
                        from fields.inline_text_field import InlineTextField
                        inline_field = InlineTextField(self, c)
                        inline_field.draw_field(field_name, label)
                    else:
                        from fields.text_field import TextField
                        text_field = TextField(self, c)
                        text_field.draw(field_name, label)
                elif field_type == 'select':
                    from fields.select_field import SelectField
                    select_field = SelectField(self, c)
                    select_field.draw(field_name, label, options)
                elif field_type == 'textarea':
                    from fields.text_area import TextArea
                    text_area = TextArea(self, c)
                    text_area.draw(field_name, label)
                elif field_type == 'radio':
                    from fields.radio_button import RadioButton
                    radio_button = RadioButton(self, c)
                    radio_button.draw(field_name, label, options)
                elif field_type == 'checkbox':
                    from fields.check_box import CheckBox
                    check_box = CheckBox(self, c)
                    check_box.draw(field_name, label, options)
                else:
                    # Fallback for unknown field types
                    from fields.text_field import TextField
                    text_field = TextField(self, c)
                    text_field.draw(field_name, label)
            except Exception as e:
                print(f"Error drawing field '{field_name}' of type '{field_type}': {e}")
                # Fallback to text field
                from fields.text_field import TextField
                text_field = TextField(self, c)
                text_field.draw(field_name, f"{label} (Error: treated as text)")
                    
        c.setFont(current_font, current_size)
        c.setFillColor(current_color)
        
    def _handle_group_page_break(self, c):
        """Handle page breaks when in a group - preserve group state"""
        if self.current_group is not None:
            # Store current group info
            temp_group = self.current_group
            temp_config = {
                'columns': self.group_columns,
                'widths': [w / (self.field_width - self.group_spacing * (self.group_columns - 1))
                        for w in self.column_widths] if self.column_widths else [0.5, 0.5],
                'spacing': self.group_spacing
            }

            # End current group
            from fields.group_field import GroupField
            group_field = GroupField(self, c)
            group_field.end_group()

            # Start new page
            self.current_page += 1
            self.page_manager.initialize_page(c)

            # Restart the group on new page
            group_field.start_group(temp_group)
        else:
            # Normal page break
            self.current_page += 1
            self.page_manager.initialize_page(c)

    def _start_auto_flow(self, c):
        """Start auto-flow 2-column layout (CSS flexbox-like behavior)"""
        if self.auto_flow_active:
            return  # Already active

        self.auto_flow_active = True
        self.auto_flow_field_count = 0

        # Use group system internally with special marker
        from fields.group_field import GroupField
        group_field = GroupField(self, c)
        group_field.start_group('__auto_flow__')

    def _end_auto_flow(self, c):
        """End auto-flow layout"""
        if not self.auto_flow_active:
            return  # Not active

        from fields.group_field import GroupField
        group_field = GroupField(self, c)
        group_field.end_group()

        self.auto_flow_active = False
        self.auto_flow_field_count = 0

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

            # --- AUTO-FLOW LOGIC: CSS flexbox-like 2-column layout for text fields ---
            # Only apply auto-flow if not inside an explicit user-defined group
            in_explicit_group = (self.current_group is not None and
                                self.current_group != '__auto_flow__')

            if not in_explicit_group:
                is_flowable = field_type in AUTO_FLOW_FIELD_TYPES
                is_flow_breaker = field_type in FLOW_BREAK_FIELD_TYPES

                if is_flowable:
                    # Start auto-flow if not already active
                    if not self.auto_flow_active:
                        self._start_auto_flow(c)
                    self.auto_flow_field_count += 1
                elif is_flow_breaker:
                    # End auto-flow before drawing flow-breaking field
                    if self.auto_flow_active:
                        self._end_auto_flow(c)

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

                # Temporarily end current group if any (including auto-flow)
                temp_group = self.current_group
                was_auto_flow = self.auto_flow_active
                if self.current_group:
                    group_field = GroupField(self, c)
                    group_field.end_group()
                    self.current_group = None
                    if was_auto_flow:
                        self.auto_flow_active = False

                # Draw the field as full-width
                self._draw_field(c, field_type, field_name, label, field.get('option', {}))
                i += 1

                # Restore the group if we temporarily ended it (but not auto-flow)
                if temp_group and not was_auto_flow:
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

        # End auto-flow if still active at end of form
        if self.auto_flow_active:
            self._end_auto_flow(c)

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
        self.group_stack = []
        self.inline_state = None
        self.auto_flow_active = False
        self.auto_flow_field_count = 0
        
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
def generate_form_pdf(json_file_path, output_pdf_path, business_info=None):
    """Generate form PDF from JSON file.

    Args:
        json_file_path: Path to the JSON form definition
        output_pdf_path: Path for the output PDF
        business_info: Optional dict with keys: logo_path, business_name, address, phone, email
    """
    if not os.path.exists(json_file_path):
        raise FileNotFoundError(f"JSON file not found: {json_file_path}")

    with open(json_file_path, 'r', encoding='utf-8') as file:
        form_data = json.load(file)

    generator = ModernPDFFormGenerator(form_data, business_info=business_info)
    generator.generate_pdf(output_pdf_path)


if __name__ == "__main__":
    import glob

    # Paths
    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
    INPUT_DIR = os.path.join(SCRIPT_DIR, 'form', 'input')
    OUTPUT_DIR = '/Users/camerondyas/Desktop/CustomPDF'

    # Load business info from input folder if available
    business_info_path = os.path.join(INPUT_DIR, 'business_info.json')
    business_info = None

    if os.path.exists(business_info_path):
        try:
            with open(business_info_path, 'r', encoding='utf-8') as f:
                business_info = json.load(f)
            print(f"Loaded business info: {business_info.get('business_name', 'Unknown')}")
        except Exception as e:
            print(f"Warning: Could not load business_info.json: {e}")
            print("Using default business info from constants.py")

    # Use logo from CustomPDF folder if available
    logo_path = "/Users/camerondyas/Desktop/CustomPDF/logo.png"

    # Find JSON files in the input folder (exclude business_info.json)
    json_files = [f for f in glob.glob(os.path.join(INPUT_DIR, '*.json'))
                  if os.path.basename(f) != 'business_info.json']

    if not json_files:
        print(f"No form JSON files found in: {INPUT_DIR}")
        print("Place your form JSON files in the input folder and run again.")
        exit(1)

    print(f"Found {len(json_files)} form JSON file(s) to process")

    for json_path in json_files:
        json_filename = os.path.basename(json_path)
        pdf_filename = os.path.splitext(json_filename)[0] + '.pdf'
        output_path = os.path.join(OUTPUT_DIR, pdf_filename)

        print(f"\nProcessing: {json_filename}")
        print(f"  Output: {output_path}")

        try:
            if os.path.exists(output_path):
                os.remove(output_path)
                print(f"  Deleted existing: {pdf_filename}")

            generate_form_pdf(json_path, output_path, business_info=business_info)
            print(f"  PDF generated successfully!")

            # Delete the input JSON file after successful processing
            os.remove(json_path)
            print(f"  Cleaned up input file: {json_filename}")

        except FileNotFoundError as e:
            print(f"  File error: {e}")
        except json.JSONDecodeError as e:
            print(f"  JSON parsing error: {e}")
        except KeyError as e:
            print(f"  Missing required data in JSON: {e}")
        except Exception as e:
            print(f"  Error generating PDF: {e}")
            import traceback
            traceback.print_exc()

    # Clean up business_info.json after processing
    if os.path.exists(business_info_path):
        os.remove(business_info_path)
        print(f"\nCleaned up: business_info.json")

    print(f"\nDone! PDFs saved to: {OUTPUT_DIR}")