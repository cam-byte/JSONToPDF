# constants.py - CLEAN READABLE LAYOUT
from reportlab.lib import colors
import os

# Reasonable margins for clean layout
MARGINS = {
    'x': 60,  # Reasonable margin
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
        'widths': [0.4, 0.4, 0.2],  # First Name (40%), Last Name (40%), Middle (20%)
        'spacing': 8  # Increased spacing to prevent overlap
    },
    'contact_information': {
        'columns': 4,  # Changed from 2 to 4 to handle the 4 fields you have
        'widths': [0.25, 0.25, 0.25, 0.25],  # Equal width for home/cell/work phone + preferred contact
        'spacing': 15
    },
    'address_details': {
        'columns': 4,
        'widths': [0.5, 0.2, 0.15, 0.15],  # Address (50%), City (20%), State (15%), Zip (15%)
        'spacing': 12  # Slightly more spacing
    },
    'guardian_details': {
        'columns': 2,
        'widths': [0.5, 0.5],
        'spacing': 20  # More spacing
    },
    'two_columns': {
        'columns': 2,
        'widths': [0.45, 0.45],  # Slightly less than 50% each to account for spacing
        'spacing': 30  # More spacing to prevent overlap
    },
    'four_columns': {
        'columns': 4,
        'widths': [0.23, 0.23, 0.23, 0.23],  # Slightly less than 25% each
        'spacing': 15
    },
    'substance_details': {
        'columns': 1,
        'widths': [1.0],
        'spacing': 0
    },
    'women_only': {
        'columns': 1,
        'widths': [1],
        'spacing': 20
    },
    'pharmacy_information': {
        'columns': 1,
        'widths': [1.0],
        'spacing': 0
    }
}