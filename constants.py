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
    'business_name': 'Dr. Effie Deegan',
    'address': '23 Old Short Hills Rd, West Orange, NJ 07052',
    'phone': '(973) 736-4432',
    'email': 'frontdesk@deegandental.com'
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
    'other_disease',      # Radio button that should be full width
    'premedication_required',  # Radio button that should be full width
}

# Clean group configurations with reasonable spacing
# constants.py - FIXED FOR ACTUAL JSON STRUCTURE

GROUP_CONFIGS = {
    # Container groups (allow nesting)
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
    'primary_insurance': {
        'columns': 1,
        'widths': [1.0],
        'spacing': 0
    },
    
    # Functional groups (the ones that actually control layout)
    'name_details': {
        'columns': 3,
        'widths': [0.43, 0.43, 0.14],  # Last name, First name, Initial
        'spacing': 8
    },
    'address_details': {
        'columns': 4,
        'widths': [0.5, 0.2, 0.1, 0.2],  # Address, City, State, Zip
        'spacing': 12
    },
    'patient_contact': {
        'columns': 3,
        'widths': [0.33, 0.33, 0.34],  # Email, Business Phone, Cell Phone
        'spacing': 10
    },
    'phone_details': {
        'columns': 3,
        'widths': [0.33, 0.33, 0.34],
        'spacing': 10
    },
    'secondary_insurance': {
        'columns': 2,
        'widths': [0.5, 0.5],
        'spacing': 15
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
    
    # Special groups
    'women_only': {
        'columns': 1,
        'widths': [1.0],
        'spacing': 20
    },
    
    # Dental chart groups (if needed)
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
        'columns': 1,
        'widths': [1.0],
        'spacing': 0
    },
    'tooth': {
        'columns': 1,
        'widths': [1.0],
        'spacing': 2
    },
    
    # Other utility groups
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
    'pharmacy_information': {
        'columns': 1,
        'widths': [1.0],
        'spacing': 0
    }
}