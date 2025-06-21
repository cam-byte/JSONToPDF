# fields/check_box.py - DYNAMIC SPACING VERSION

from utils import _get_options, _strip_html_tags, wrap_text

class CheckBox:
    def __init__(self, generator, canvas):
        self.generator = generator
        self.canvas = canvas
        self.colors = generator.colors
        self.margin_x = generator.margin_x
        self.field_width = generator.field_width

    def draw(self, field_name, label, options):
        c = self.canvas
        current_font = c._fontname
        current_size = c._fontsize
        current_color = c._fillColorObj

        self.current_options = options

        # DYNAMIC SPACING: Calculate spacing based on context
        spacing = self._calculate_dynamic_spacing(field_name, label, options)
        self.generator.current_y -= spacing

        # Calculate field positioning
        field_x, field_width, field_y = self._get_field_position()
        starting_y = field_y

        # Get checkbox options
        options_list = _get_options(options)

        if len(options_list) == 1:
            self._draw_single_checkbox(c, field_name, label, field_x, field_width, field_y, starting_y)
        else:
            self._draw_multiple_checkboxes(c, field_name, label, options_list, field_x, field_width, field_y, starting_y)

        c.setFont(current_font, current_size)
        c.setFillColor(current_color)

    def _calculate_dynamic_spacing(self, field_name, label, options):
        """Calculate appropriate spacing based on checkbox context"""
        base_spacing = 10  # Minimum spacing
        
        # Get the checkbox text to analyze
        checkbox_text = self._get_checkbox_text(label, options)
        
        # Factor 1: Text length - longer text needs more spacing
        if len(checkbox_text) > 200:
            text_spacing = 25  # Very long text (like acknowledgements)
        elif len(checkbox_text) > 100:
            text_spacing = 15  # Medium long text
        else:
            text_spacing = 5   # Short text
        
        # Factor 2: Check what came before this checkbox
        previous_element_spacing = self._get_previous_element_spacing()
        
        # Factor 3: Special cases based on field name
        special_spacing = 0
        if 'acknowledgement' in field_name.lower():
            special_spacing = 20  # Acknowledgements need extra space
        elif 'signature' in field_name.lower():
            special_spacing = 15  # Signature-related checkboxes
        
        # Factor 4: If checkbox has no label but long text in options
        label_spacing = 0
        if not label or not label.strip():
            if len(checkbox_text) > 50:
                label_spacing = 10  # No label but long text
        
        # Combine all factors, but cap at reasonable maximum
        total_spacing = base_spacing + text_spacing + previous_element_spacing + special_spacing + label_spacing
        return min(total_spacing, 60)  # Cap at 60 points max

    def _get_checkbox_text(self, label, options):
        """Extract the actual text that will be displayed with the checkbox"""
        checkbox_text = label or ""
        
        if not checkbox_text or not checkbox_text.strip():
            if options and isinstance(options, dict):
                if 'checked' in options:
                    checkbox_text = options['checked']
                elif len(options) == 1:
                    checkbox_text = list(options.values())[0]
        
        return _strip_html_tags(checkbox_text or "")

    def _get_previous_element_spacing(self):
        """Determine additional spacing needed based on what came before"""
        # This would require tracking the previous element type
        # For now, we can use a simple heuristic based on current Y position
        # relative to where we started on the page
        
        page_start_y = self.generator.page_height - self.generator.margin_x
        distance_from_top = page_start_y - self.generator.current_y
        
        # If we're near the top of a page, likely following a header
        if distance_from_top < 100:
            return 5  # Less spacing needed
        else:
            return 10  # Standard spacing
        
        # TODO: Could enhance this by tracking previous field types
        # in the generator and adjusting spacing accordingly

    def _draw_single_checkbox(self, c, field_name, label, field_x, field_width, field_y, starting_y):
        # Extract checkbox text
        checkbox_text = self._get_checkbox_text(label, self.current_options)

        style = self.generator.label_manager.get_label_style('checkbox', checkbox_text)
        font_name = style.font_name
        font_size = style.font_size
        color = style.color

        # Checkbox settings
        checkbox_size = 12
        checkbox_y_top = self.generator.current_y
        checkbox_y = checkbox_y_top - checkbox_size + 2

        # Calculate text dimensions and check for page breaks
        text_x = field_x + checkbox_size + 8
        max_width = self.generator.page_width - text_x - self.generator.margin_x

        lines, total_text_height = wrap_text(c, checkbox_text, max_width, font_name, font_size)
        needed_height = max(checkbox_size, total_text_height) + 20

        # Page break check
        if checkbox_y - needed_height < self.generator.margin_bottom:
            from utils import _check_page_break
            if _check_page_break(self.generator, c, needed_height + 20):
                self.generator.page_manager.initialize_page(c)
                checkbox_y_top = self.generator.current_y
                checkbox_y = checkbox_y_top - checkbox_size + 2

        # Draw checkbox
        c.acroForm.checkbox(
            name=field_name,
            tooltip=checkbox_text[:50] + "..." if len(checkbox_text) > 50 else checkbox_text,
            x=field_x,
            y=checkbox_y,
            size=checkbox_size,
            borderColor=self.colors['border'],
            fillColor=self.colors['background'],
            textColor=self.colors['primary'],
            borderWidth=0.5,
            checked=False
        )

        # Draw text
        c.setFont(font_name, font_size)
        c.setFillColor(color)
        
        text_y = checkbox_y_top
        for line in lines:
            c.drawString(text_x, text_y, line)
            text_y -= font_size + 4

        # Calculate final position with dynamic spacing after
        after_spacing = 15 if len(checkbox_text) > 100 else 8
        final_y = text_y - after_spacing
        self.generator.current_y = final_y

        if self.generator.current_group is not None:
            self.generator.group_fields.append({'y': final_y, 'name': field_name})

    def _draw_multiple_checkboxes(self, c, field_name, label, options_list, field_x, field_width, field_y, starting_y):
        # Draw main label if present
        if label and label.strip():
            style = self.generator.label_manager.get_label_style('checkbox', label)
            self.generator.label_manager.draw_label(c, label, style)
            self.generator.current_y -= 8

        current_y = self.generator.current_y
        c.setFont("Helvetica", 9)
        c.setFillColor(self.colors['primary'])

        # Layout settings
        checkbox_size = 12
        padding = 6
        option_spacing = 30
        max_label_width = 80

        available_width = field_width
        start_x = field_x
        current_x = start_x

        from reportlab.pdfbase.pdfmetrics import stringWidth
        row_max_height = checkbox_size

        for i, (value, option_label) in enumerate(options_list):
            clean_option_label = _strip_html_tags(option_label)
            label_width = min(stringWidth(clean_option_label, "Helvetica", 9), max_label_width)
            total_width = checkbox_size + padding + label_width + option_spacing

            if current_x + total_width > start_x + available_width:
                current_x = start_x
                current_y -= (row_max_height + 8)
                row_max_height = checkbox_size

            checkbox_name = f"{field_name}_{value}"
            c.acroForm.checkbox(
                name=checkbox_name,
                tooltip=f"{field_name} - {clean_option_label}",
                x=current_x,
                y=current_y - checkbox_size + 2,
                size=checkbox_size,
                borderColor=self.colors['border'],
                fillColor=self.colors['background'],
                textColor=self.colors['primary'],
                borderWidth=0.5,
                checked=False
            )

            label_x = current_x + checkbox_size + padding
            label_y = current_y
            c.drawString(label_x, label_y, clean_option_label)
            current_x += total_width

        final_field_y = current_y - row_max_height - 12

        if self.generator.current_group is not None:
            self._handle_group_positioning(field_x, field_width, final_field_y, starting_y)
        else:
            self.generator.current_y = final_field_y

    def _get_field_position(self):
        """Calculate position for field within group or regular flow"""
        field_x = self.margin_x
        field_width = self.field_width
        field_y = self.generator.current_y

        if self.generator.current_group is not None:
            group_index = len(self.generator.group_fields)
            column_index = group_index % self.generator.group_columns

            field_x = self.margin_x
            if column_index > 0:
                field_x += sum(self.generator.column_widths[:column_index])
                field_x += self.generator.group_spacing * column_index

            field_width = self.generator.column_widths[column_index]

            if column_index > 0 and self.generator.group_fields:
                row_index = group_index // self.generator.group_columns
                first_in_row_index = row_index * self.generator.group_columns
                if first_in_row_index < len(self.generator.group_fields):
                    first_field = self.generator.group_fields[first_in_row_index]
                    field_y = first_field.get('start_y', first_field.get('y', field_y))

        return field_x, field_width, field_y

    def _handle_group_positioning(self, field_x, field_width, final_y, start_y):
        """Handle positioning when field is in a group"""
        self.generator.group_fields.append({
            'name': 'checkbox',
            'x': field_x,
            'y': final_y,
            'start_y': start_y,
            'width': field_width
        })

        if len(self.generator.group_fields) % self.generator.group_columns == 0:
            row_start = len(self.generator.group_fields) - self.generator.group_columns
            row_fields = self.generator.group_fields[row_start:]
            min_y = min(f.get('y', self.generator.current_y) for f in row_fields)
            self.generator.current_y = min_y - 12