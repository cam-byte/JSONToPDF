# constants.py - CLEAN READABLE LAYOUT
from reportlab.lib import colors
import os

# Reasonable margins for clean layout
MARGINS = {
    'x': 50,  # Reasonable margin
    'bottom': 60  # Reasonable bottom margin
}

# Normal field dimensions
FIELD_DIMENSIONS = {
    'width': 510,
    'height': 18  # Slightly smaller but readable
}

# Logo path handling
logo_candidates = [
    '/Users/camerondyas/Documents/scripts/pythonScripts/JSONToPDF/logo.png',
    './logo.png',
    './assets/logo.png',
    None
]

logo_path = None
for path in logo_candidates:
    if path and os.path.exists(path):
        logo_path = path
        break

BUSINESS_INFO = {
    'logo_path': logo_path,
    'business_name': 'Your Dental Practice',
    'address': '123 Main Street, City, State 12345',
    'phone': '(555) 123-4567',
    'email': 'info@yourpractice.com'
}

COLORS = {
    'primary': colors.black,
    'secondary': colors.Color(0.4, 0.4, 0.4),
    'accent': colors.Color(0.2, 0.4, 0.8),
    'border': colors.Color(0.7, 0.7, 0.7),
    'background': colors.white
}

# Fields that should break out of groups and be full-width
FULL_WIDTH_FIELDS = {
    'preferred_contact',  # Preferred Method of Contact radio button
    'acknowledgement',    # Acknowledgement checkbox with paragraph text
    # Add more field names here as needed:
    # 'special_instructions',
    # 'emergency_contact_notes',
}

# Clean group configurations with reasonable spacing
# constants.py - FIXED FOR ACTUAL JSON STRUCTURE

GROUP_CONFIGS = {
    'form_container': {
        'columns': 1,
        'widths': [1.0],
        'spacing': 0
    },
    'form_content_container': {
        'columns': 1,
        'widths': [1.0],
        'spacing': 0
    },
    'name_details': {
        'columns': 3,
        'widths': [0.43, 0.43, 0.14],
        'spacing': 8
    },
    '*name_details': {
        'columns': 3,
        'widths': [0.43, 0.43, 0.14],
        'spacing': 8
    },
    'phone_details': {
        'columns': 3,
        'widths': [0.33, 0.33, 0.34],
        'spacing': 10
    },
    'address_details': {
        'columns': 4,
        'widths': [0.5, 0.2, 0.1, 0.2],
        'spacing': 12
    },
    'two_columns': {
        'columns': 2,
        'widths': [0.5, 0.5],
        'spacing': 20
    },
    'four_columns': {
        'columns': 4,
        'widths': [0.25, 0.25, 0.25, 0.25],
        'spacing': 15
    },
    # Dental chart - FIXED to match your JSON structure
    'permanent': {
        'columns': 1,
        'widths': [1.0],
        'spacing': 0
    },
    'deciduous': {
        'columns': 1,
        'widths': [1.0],
        'spacing': 0
    },
    'top_row': {
        'columns': 1,
        'widths': [1.0],
        'spacing': 0
    },
    'bottom_row': {
        'columns': 1,
        'widths': [1.0],
        'spacing': 0
    },
    'tooth_container': {
        'columns': 1,  # FIXED: This contains the row, not individual teeth
        'widths': [1.0],
        'spacing': 0
    },
    'tooth': {
        'columns': 1,  # FIXED: Each tooth is individual, not 16 columns
        'widths': [1.0],
        'spacing': 2  # Minimal spacing between individual teeth
    },
    # Other groups
    'indent_x1': {
        'columns': 1,
        'widths': [1.0],
        'spacing': 0
    },
    'substance_details': {
        'columns': 1,
        'widths': [1.0],
        'spacing': 0
    },
    'women_only': {
        'columns': 1,
        'widths': [1.0],
        'spacing': 20
    },
    'pharmacy_information': {
        'columns': 1,
        'widths': [1.0],
        'spacing': 0
    }
}