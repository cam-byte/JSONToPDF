# constants.py - CLEAN READABLE LAYOUT
from reportlab.lib import colors
import os

# Reasonable margins for clean layout
MARGINS = {
    'x': 60,          # Reasonable margin
    'bottom': 60      # Reasonable bottom margin
}

# Normal field dimensions
FIELD_DIMENSIONS = {
    'width': 450,
    'height': 18      # Slightly smaller but readable
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

# Clean group configurations with reasonable spacing
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
    '*name_details': {
        'columns': 3,
        'widths': [0.4, 0.4, 0.2],
        'spacing': 15
    },
    'contact_information': {
        'columns': 2,
        'widths': [0.5, 0.5],
        'spacing': 15
    },
    '*address_details': {
        'columns': 4,
        'widths': [0.5, 0.2, 0.15, 0.15],
        'spacing': 10
    },
    'guardian_details': {
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
        'spacing': 10
    },
    'substance_details': {
        'columns': 1,
        'widths': [1.0],
        'spacing': 0
    },
    'women_only': {
        'columns': 2,
        'widths': [0.5, 0.5],
        'spacing': 15
    },
    'pharmacy_information': {
        'columns': 1,
        'widths': [1.0],
        'spacing': 0
    }
}