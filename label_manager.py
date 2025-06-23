# label_manager.py - Enhanced version with link and list support
import re
from utils import _strip_html_tags, _wrap_text

class LabelManager:
    def __init__(self, generator):
        self.generator = generator
        self.label_styles = generator.label_styles
        self.margin_x = generator.margin_x
        self.field_width = generator.field_width
        self.colors = generator.colors

    def get_label_style(self, field_type, label):
        """Determine the appropriate label style based on content"""
        if field_type == 'label':
            if '<h1>' in label.lower():
                return self.label_styles['h1']
            elif '<h3>' in label.lower():
                return self.label_styles['h3']
            elif '<h4>' in label.lower():
                return self.label_styles['h4']
            elif '<h5>' in label.lower():
                return self.label_styles['h5']
            elif '<p>' in label.lower():
                # Check if there are lists INSIDE the paragraph (both ul and ol)
                if '<ul>' in label.lower() or '<li>' in label.lower() or '<ol>' in label.lower():
                    return self.label_styles.get('ul', self.label_styles['p'])
                else:
                    return self.label_styles['p']
            elif '<ul>' in label.lower() or '<li>' in label.lower() or '<ol>' in label.lower():
                return self.label_styles.get('ul', self.label_styles['p'])
            else:
                return self.label_styles['regular']
        else:
            return self.label_styles['field_label']

    def _extract_link_text(self, html_text):
        """Extract text from links, preserving just the inner HTML of <a> tags"""
        # Pattern to match <a> tags and capture their inner content
        link_pattern = r'<a[^>]*>(.*?)</a>'
        
        def replace_link(match):
            return match.group(1)  # Return just the inner content
        
        return re.sub(link_pattern, replace_link, html_text, flags=re.IGNORECASE | re.DOTALL)

    def _process_list_content(self, html_text):
        """Process <ul>/<ol> and <li> tags to create formatted list text"""
        print(f"DEBUG: Processing list content, length: {len(html_text)}")
        
        # Check if this is an ordered list (ol) or unordered list (ul)
        is_ordered_list = '<ol>' in html_text.lower() or '<ol ' in html_text.lower()
        
        # Don't extract from <p> tags when we have mixed content with lists
        # Instead, process the entire content to preserve <ol>/<ul> sections
        text = html_text
        
        # Remove <p> and </p> tags but keep the content
        text = re.sub(r'<p[^>]*>', '\n\n', text, flags=re.IGNORECASE)
        text = re.sub(r'</p>', '', text, flags=re.IGNORECASE)
        
        # Remove <ul>, </ul>, <ol>, and </ol> tags
        text = re.sub(r'</?[uo]l[^>]*>', '\n', text, flags=re.IGNORECASE)
        
        # Replace <li> tags with appropriate markers
        if is_ordered_list:
            # For ordered lists, we'll use a placeholder that we'll replace with numbers
            text = re.sub(r'<li[^>]*>', '\n##LISTITEM##', text, flags=re.IGNORECASE)
        else:
            # For unordered lists, use bullet points
            text = re.sub(r'<li[^>]*>', '\n• ', text, flags=re.IGNORECASE)
        
        text = re.sub(r'</li>', '', text, flags=re.IGNORECASE)
        
        # Clean up extra whitespace but preserve line breaks
        lines = text.split('\n')
        processed_lines = []
        list_counter = 1
        
        for line in lines:
            line = line.strip()
            if line:
                if line.startswith('##LISTITEM##'):
                    # Replace placeholder with numbered list item
                    line = f"{list_counter}. " + line[12:]  # Remove ##LISTITEM## and add number
                    list_counter += 1
                processed_lines.append(line)
        
        result = '\n'.join(processed_lines)
        print(f"DEBUG: Final processed result: {result[:400]}...")
        return result

    def _clean_html_content(self, html_text):
        """Clean HTML content by handling links and lists before stripping tags"""
        # First, extract link text (preserve inner HTML of <a> tags)
        text = self._extract_link_text(html_text)
        
        # Handle lists if present (both ul and ol)
        if '<ul>' in text.lower() or '<li>' in text.lower() or '<ol>' in text.lower():
            text = self._process_list_content(text)
        
        # Finally strip remaining HTML tags
        return _strip_html_tags(text)

    def draw_label(self, canvas, label, style, draw_line=False, spacing_before=None):
        """Draw label with enhanced HTML processing"""
        self._draw_enhanced_label(canvas, label, style, draw_line, spacing_before)

    def _draw_enhanced_label(self, canvas, label, style, draw_line=False, spacing_before=None):
        """Enhanced label drawing with link and list support"""
        current_font = canvas._fontname
        current_size = canvas._fontsize
        current_color = canvas._fillColorObj

        # Clean the label text using enhanced HTML processing
        clean_text = self._clean_html_content(label)

        # Skip empty labels
        if not clean_text.strip():
            return

        # Apply spacing_before if provided, otherwise use style's spacing_before
        if spacing_before is not None:
            self.generator.current_y -= spacing_before
        elif hasattr(style, 'spacing_before'):
            self.generator.current_y -= style.spacing_before

        # Set font and color
        canvas.setFont(style.font_name, style.font_size)
        canvas.setFillColor(style.color)

        # Determine content type - lists take absolute priority (both ul and ol)
        is_list = "<ul>" in label.lower() or "<li>" in label.lower() or "<ol>" in label.lower()
        is_paragraph = "<p>" in label.lower() and "</p>" in label.lower() and not is_list

        # Use full page width for paragraphs and lists, field width for others
        if is_paragraph or is_list:
            wrap_width = self.generator.page_width - 2 * self.generator.margin_x
            line_height = style.font_size + 6  # Increased line height for paragraphs and lists
        else:
            wrap_width = self.field_width
            line_height = style.font_size + 1  # Normal line height for other labels

        # Handle paragraph margins if applicable
        if (is_paragraph or is_list) and hasattr(style, 'paragraph_margin_top'):
            self.generator.current_y -= style.paragraph_margin_top

        # For lists, we need to handle each line separately to preserve bullet formatting
        if is_list:
            self._draw_list_content(canvas, clean_text, style, wrap_width, line_height)
        else:
            # Regular text wrapping for non-list content
            wrapped_lines = _wrap_text(clean_text, wrap_width, style.font_size, style.font_name)
            self._draw_text_lines(canvas, wrapped_lines, line_height)

        # Handle margins and underlines
        if (is_paragraph or is_list) and hasattr(style, 'paragraph_margin_bottom'):
            self.generator.current_y -= style.paragraph_margin_bottom

        # Draw underline for h1 headers if requested
        if draw_line and clean_text.strip():
            line_y = self.generator.current_y + line_height + 7
            canvas.setStrokeColor(self.colors['accent'])
            canvas.setLineWidth(1)
            canvas.line(self.margin_x, line_y, self.margin_x + wrap_width, line_y)

        # Restore original settings
        canvas.setFont(current_font, current_size)
        canvas.setFillColor(current_color)

    def _draw_list_content(self, canvas, text, style, wrap_width, line_height):
        """Draw list content with proper bullet point or numbered formatting"""
        lines = text.split('\n')
        lines_drawn = 0
        
        for line in lines:
            line = line.strip()
            if not line:
                # Empty line - add some spacing for paragraph breaks
                self.generator.current_y -= line_height // 2
                continue
                
            # Check if this is a list item (bullet or numbered)
            is_bullet_item = line.startswith('•')
            is_numbered_item = re.match(r'^\d+\.\s', line)
            
            if is_bullet_item or is_numbered_item:
                # This is a list item
                if is_bullet_item:
                    marker_part = '• '
                    text_part = line[2:].strip()  # Remove bullet and leading space
                else:  # numbered item
                    # Extract the number and period (e.g., "1. ")
                    match = re.match(r'^(\d+\.\s)(.*)', line)
                    marker_part = match.group(1)
                    text_part = match.group(2)
                
                # Draw marker (bullet or number)
                canvas.drawString(self.margin_x, self.generator.current_y, marker_part)
                
                # Calculate indent for text after marker
                marker_width = canvas.stringWidth(marker_part, style.font_name, style.font_size)
                text_indent = self.margin_x + marker_width
                text_wrap_width = wrap_width - marker_width
                
                # Wrap the text part
                if text_part:
                    wrapped_text_lines = _wrap_text(text_part, text_wrap_width, style.font_size, style.font_name)
                    
                    # Draw first line on same line as marker
                    if wrapped_text_lines:
                        canvas.drawString(text_indent, self.generator.current_y, wrapped_text_lines[0])
                        self.generator.current_y -= line_height
                        lines_drawn += 1
                        
                        # Draw continuation lines with same indent
                        for wrapped_line in wrapped_text_lines[1:]:
                            canvas.drawString(text_indent, self.generator.current_y, wrapped_line)
                            self.generator.current_y -= line_height
                            lines_drawn += 1
                else:
                    # Just marker, no text
                    self.generator.current_y -= line_height
                    lines_drawn += 1
            else:
                # Regular paragraph text (not a list item)
                wrapped_lines = _wrap_text(line, wrap_width, style.font_size, style.font_name)
                for wrapped_line in wrapped_lines:
                    if wrapped_line.strip():
                        canvas.drawString(self.margin_x, self.generator.current_y, wrapped_line)
                        self.generator.current_y -= line_height
                        lines_drawn += 1

        # Add spacing after list
        if lines_drawn > 0:
            self.generator.current_y -= style.spacing_after

    def _draw_text_lines(self, canvas, wrapped_lines, line_height):
        """Draw regular text lines"""
        lines_drawn = 0
        
        for line in wrapped_lines:
            if line.strip():
                canvas.drawString(self.margin_x, self.generator.current_y, line)
                self.generator.current_y -= line_height
                lines_drawn += 1

        # Add spacing after text
        if lines_drawn > 0:
            self.generator.current_y -= self.label_styles['p'].spacing_after if hasattr(self, 'label_styles') else 5
        
    def _draw_simple_label(self, canvas, label, style, draw_line=False, spacing_before=None):
        """Fallback to original simple label drawing logic if needed"""
        current_font = canvas._fontname
        current_size = canvas._fontsize
        current_color = canvas._fillColorObj

        # Clean the label text
        clean_text = _strip_html_tags(label)

        # Skip empty labels
        if not clean_text.strip():
            return

        # Apply spacing_before if provided, otherwise use style's spacing_before
        if spacing_before is not None:
            self.generator.current_y -= spacing_before
        elif hasattr(style, 'spacing_before'):
            self.generator.current_y -= style.spacing_before

        # Set font and color
        canvas.setFont(style.font_name, style.font_size)
        canvas.setFillColor(style.color)

        # Determine if this is a paragraph
        is_paragraph = "<p>" in label.lower() and "</p>" in label.lower()

        # Use full page width for paragraphs, field width for others
        if is_paragraph:
            wrap_width = self.generator.page_width - 2 * self.generator.margin_x
            line_height = style.font_size + 6  # Increased line height for paragraphs
        else:
            wrap_width = self.field_width
            line_height = style.font_size + 1  # Normal line height for other labels

        wrapped_lines = _wrap_text(clean_text, wrap_width, style.font_size, style.font_name)

        # Handle paragraph margins if applicable
        if is_paragraph and hasattr(style, 'paragraph_margin_top'):
            self.generator.current_y -= style.paragraph_margin_top

        # Draw each line
        current_line_y = self.generator.current_y
        lines_drawn = 0

        for line in wrapped_lines:
            if line.strip():
                canvas.drawString(self.margin_x, current_line_y, line)
                current_line_y -= line_height
                lines_drawn += 1

        # Minimal spacing after labels
        if lines_drawn > 0:
            actual_text_height = lines_drawn * line_height
            self.generator.current_y = self.generator.current_y - actual_text_height - style.spacing_after
        else:
            # Even for empty content, minimal movement
            self.generator.current_y -= style.spacing_after

        if is_paragraph and hasattr(style, 'paragraph_margin_bottom'):
            self.generator.current_y -= style.paragraph_margin_bottom

        # Draw underline for h1 headers if requested
        if draw_line and lines_drawn > 0:
            line_y = current_line_y + line_height - 5
            canvas.setStrokeColor(self.colors['accent'])
            canvas.setLineWidth(1)  # Thinner line
            canvas.line(self.margin_x, line_y, self.margin_x + wrap_width, line_y)

        # Restore original settings
        canvas.setFont(current_font, current_size)
        canvas.setFillColor(current_color)