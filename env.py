# env.py - Configuration file for paths
import os

# Default paths
DEFAULT_JSON_PATH = '/Users/camerondyas/Documents/scripts/pythonScripts/JSONToPDF/form/form.json'
DEFAULT_PDF_PATH = '/Users/camerondyas/Documents/scripts/pythonScripts/JSONToPDF/form/generated_form.pdf'

# Environment variable keys
JSON_INPUT_PATH_KEY = 'JSON_INPUT_PATH'
PDF_OUTPUT_PATH_KEY = 'PDF_OUTPUT_PATH'

def get_json_input_path():
    """Get JSON input path from environment or return default"""
    return os.getenv(JSON_INPUT_PATH_KEY, DEFAULT_JSON_PATH)

def get_pdf_output_path():
    """Get PDF output path from environment or return default"""
    return os.getenv(PDF_OUTPUT_PATH_KEY, DEFAULT_PDF_PATH)

# For direct access
JSON_INPUT_PATH = get_json_input_path()
PDF_OUTPUT_PATH = get_pdf_output_path()