# constants.py
from reportlab.lib import colors

MARGINS = {
    'x': 36,
    'bottom': 36
}

FIELD_DIMENSIONS = {
    'width': 550,
    'height': 24
}

BUSINESS_INFO = {
    'address': '123 Main St, Anytown, USA 12345',
    'phone': '(555) 555-5555',
    'email': 'contact@business.com',
    'name': 'Business Name',
    'logo_path': '/Users/camerondyas/Documents/scripts/pythonScripts/JSONToPDF/form/logo.png',
    'business_name': 'Business Name'
}

COLORS = {
    'primary': colors.HexColor('#2D3748'),
    'secondary': colors.HexColor('#4A5568'),
    'accent': colors.HexColor('#3182CE'),
    'border': colors.HexColor('#E2E8F0'),
    'background': colors.HexColor('#F7FAFC'),
}

GROUP_CONFIGS = {
    '*name_details': {
        'columns': 3,
        'widths': [4, 4, 2],
        'spacing': 15
    },
    'contact_information': {
        'columns': 3,
        'widths': [3, 3, 3],
        'spacing': 15
    }
}