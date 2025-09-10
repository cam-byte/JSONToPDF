# fields/check_box.py
# FIXED: robust option parsing -> (key, label)
# FIXED: field names = f"{field_name}_{key}"
# FIXED: tries to set export value to the full name (fallback-safe)

from utils import _strip_html_tags, wrap_text, create_acrobat_compatible_field, _check_page_break


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
        print(f"[CheckBox] draw() field='{field_name}' label='{label}' options(raw)={options}")

        # Dynamic spacing
        spacing = self._calculate_dynamic_spacing(field_name, label, options)
        self.generator.current_y -= spacing

        # Positioning
        field_x, field_width, field_y = self._get_field_position()
        starting_y = field_y

        # Parse options as (key, label)
        options_list = self._options_as_key_label(options)
        print(f"[CheckBox] options_list(normalized)={options_list}")

        if len(options_list) == 1:
            self._draw_single_checkbox(c, field_name, label, options_list, field_x, field_width, field_y, starting_y)
        else:
            self._draw_multiple_checkboxes(c, field_name, label, options_list, field_x, field_width, field_y, starting_y)

        c.setFont(current_font, current_size)
        c.setFillColor(current_color)

    # ---------- option normalization ----------

    def _options_as_key_label(self, options):
        """
        Return list[(key, label)].
        Supports:
          - {"option": {"key": "Label", ...}}
          - {"options": {"key": "Label", ...}}
          - {"key": "Label", ...}
          - [("key","Label"), ...]
          - [{"value":"key","label":"Label"}, ...]
          - ["Label1","Label2", ...] -> [("label1","Label1"), ...]
          - anything else -> [(normalized(str), str)]
        """
        # Case: full field spec with nested dict under "option" or "options"
        if isinstance(options, dict):
            nested = None
            if "option" in options and isinstance(options["option"], dict):
                nested = options["option"]
            elif "options" in options and isinstance(options["options"], dict):
                nested = options["options"]

            if nested is not None:
                return [(str(k), str(v)) for k, v in nested.items()]

            # Plain mapping of key->label
            if all(isinstance(k, (str, int)) for k in options.keys()):
                # Avoid treating field-spec dicts (with keys like name/type/label) as options
                # Heuristic: if most values are strings and keys look like identifiers, treat as options.
                keys = list(options.keys())
                # If it looks like a field spec, don't flatten it by accident
                if not {"name", "label", "email_label", "type"} & set(keys):
                    return [(str(k), str(v)) for k, v in options.items()]

        # List/tuple style
        if isinstance(options, (list, tuple)):
            out = []
            for item in options:
                if isinstance(item, tuple) and len(item) == 2:
                    k, v = item
                    out.append((str(k), str(v)))
                elif isinstance(item, dict):
                    # common schema: {"value":"key","label":"Label"}
                    if "value" in item and "label" in item:
                        out.append((str(item["value"]), str(item["label"])))
                    else:
                        # single-key dict like {"key":"Label"}
                        for k, v in item.items():
                            out.append((str(k), str(v)))
                else:
                    s = str(item)
                    out.append((self._normalize_field_value(s), s))
            return out

        # Fallback: single string or anything else
        s = str(options)
        return [(self._normalize_field_value(s), s)]

    # ---------- helpers ----------

    def _normalize_field_value(self, value):
        """Normalize to lowercase_with_underscores and strip non-alnum."""
        if value is None:
            return ""
        import re
        normalized = str(value).lower().replace(" ", "_")
        normalized = re.sub(r'[^a-z0-9_]', '_', normalized)
        normalized = re.sub(r'_+', '_', normalized)
        return normalized.strip('_')

    def _calculate_dynamic_spacing(self, field_name, label, options):
        base_spacing = 5
        checkbox_text = self._get_checkbox_text(label, options)
        if len(checkbox_text) > 200:
            text_spacing = 10
        elif len(checkbox_text) > 100:
            text_spacing = 5
        else:
            text_spacing = 0
        return min(base_spacing + text_spacing, 60)

    def _get_checkbox_text(self, label, options):
        checkbox_text = label or ""
        if not checkbox_text or not checkbox_text.strip():
            if options and isinstance(options, dict):
                if 'checked' in options:
                    checkbox_text = options['checked']
                elif len(options) == 1:
                    checkbox_text = list(options.values())[0]
        return _strip_html_tags(checkbox_text or "")

    def _create_checkbox_field(self, c, *, name, tooltip, x, y, size, checked=False, fieldFlags=0):
        """
        Wrap create_acrobat_compatible_field with a best-effort attempt to set an export value.
        Some wrappers accept export_value= or value=. If not, we fall back cleanly.
        """
        # Prefer export value as the full field name so submissions carry the full identifier
        export_val = name
        try:
            create_acrobat_compatible_field(
                c, 'checkbox',
                name=name,
                tooltip=tooltip,
                x=x, y=y, size=size,
                checked=checked,
                fieldFlags=fieldFlags,
                export_value=export_val  # try canonical kw
            )
            return
        except TypeError:
            pass

        try:
            create_acrobat_compatible_field(
                c, 'checkbox',
                name=name,
                tooltip=tooltip,
                x=x, y=y, size=size,
                checked=checked,
                fieldFlags=fieldFlags,
                value=export_val  # alternate kw some wrappers use
            )
            return
        except TypeError:
            pass

        # Final fallback: no explicit export/value support
        create_acrobat_compatible_field(
            c, 'checkbox',
            name=name,
            tooltip=tooltip,
            x=x, y=y, size=size,
            checked=checked,
            fieldFlags=fieldFlags
        )

    # ---------- drawing ----------

    def _draw_single_checkbox(self, c, field_name, label, options_list, field_x, field_width, field_y, starting_y):
        value_key, option_label = options_list[0]
        checkbox_text = _strip_html_tags(option_label)

        style = self.generator.label_manager.get_label_style('checkbox', checkbox_text)
        font_name = style.font_name
        font_size = style.font_size
        color = style.color

        checkbox_size = 12
        checkbox_y_top = self.generator.current_y
        checkbox_y = checkbox_y_top - checkbox_size + 7

        text_x = field_x + checkbox_size + 6
        max_width = self.generator.page_width - text_x - self.generator.margin_x

        lines, total_text_height = wrap_text(c, checkbox_text, max_width, font_name, font_size)
        needed_height = max(checkbox_size, total_text_height) + 20

        if checkbox_y - needed_height < self.generator.margin_bottom:
            if _check_page_break(self.generator, c, needed_height + 20):
                self.generator.page_manager.initialize_page(c)
                checkbox_y_top = self.generator.current_y
                checkbox_y = checkbox_y_top - checkbox_size + 2

        normalized_value = self._normalize_field_value(value_key)
        checkbox_name = f"{field_name}_{normalized_value}"

        self._create_checkbox_field(
            c,
            name=checkbox_name,
            tooltip=checkbox_text[:50] + "..." if len(checkbox_text) > 50 else checkbox_text,
            x=field_x,
            y=checkbox_y,
            size=checkbox_size,
            checked=False,
            fieldFlags=0
        )

        c.setFont(font_name, font_size)
        c.setFillColor(color)
        text_y = checkbox_y_top - 2
        for line in lines:
            c.drawString(text_x, text_y, line)
            text_y -= font_size + 4

        after_spacing = 15 if len(checkbox_text) > 100 else 8
        final_y = text_y - after_spacing
        self.generator.current_y = final_y

        if self.generator.current_group is not None:
            self.generator.group_fields.append({'y': final_y, 'name': field_name})

    def _calculate_optimal_spacing(self, options_list):
        from reportlab.pdfbase.pdfmetrics import stringWidth
        min_gap = 15
        checkbox_size = 12
        padding = 6

        max_label_width = 0
        for _, option_label in options_list:
            clean_label = _strip_html_tags(option_label)
            label_width = stringWidth(clean_label, "Helvetica", 9)
            max_label_width = max(max_label_width, label_width)

        item_width = checkbox_size + padding + max_label_width + min_gap
        available_width = self.field_width
        items_per_row = max(1, int(available_width / item_width))

        if len(options_list) <= items_per_row:
            return item_width

        actual_spacing = available_width / items_per_row
        min_viable = checkbox_size + padding + 30 + min_gap
        return max(actual_spacing, min_viable)

    def _draw_multiple_checkboxes(self, c, field_name, label, options_list, field_x, field_width, field_y, starting_y):
        if label and label.strip():
            style = self.generator.label_manager.get_label_style('checkbox', label)
            self.generator.label_manager.draw_label(c, label, style, spacing_before=0, tight=True)

        label_to_checkbox_gap = -12
        self.generator.current_y -= label_to_checkbox_gap

        c.setFont("Helvetica", 9)
        c.setFillColor(self.colors['primary'])

        checkbox_size = 12
        padding = 6
        row_height = checkbox_size + 8

        optimal_item_width = self._calculate_optimal_spacing(options_list)
        available_width = field_width
        start_x = field_x
        current_x = start_x
        items_per_row = max(1, int(available_width / optimal_item_width))

        items_in_current_row = 0

        for i, (value_key, option_label) in enumerate(options_list):
            clean_option_label = _strip_html_tags(option_label)

            if items_in_current_row >= items_per_row:
                current_x = start_x
                self.generator.current_y -= row_height
                items_in_current_row = 0

            checkbox_y_position = self.generator.current_y - checkbox_size + 2

            if checkbox_y_position < self.generator.margin_bottom:
                if _check_page_break(self.generator, c, checkbox_size + 20):
                    self.generator.page_manager.initialize_page(c)
                    current_x = start_x
                    items_in_current_row = 0
                    c.setFont("Helvetica", 9)
                    c.setFillColor(self.colors['primary'])

            normalized_value = self._normalize_field_value(value_key)
            checkbox_name = f"{field_name}_{normalized_value}"
            final_checkbox_y = self.generator.current_y - checkbox_size + 2

            self._create_checkbox_field(
                c,
                name=checkbox_name,
                tooltip=f"{field_name} - {clean_option_label}",
                x=current_x,
                y=final_checkbox_y,
                size=checkbox_size,
                checked=False,
                fieldFlags=0
            )

            label_x = current_x + checkbox_size + padding
            label_y = self.generator.current_y - 7
            c.drawString(label_x, label_y, clean_option_label)

            current_x += optimal_item_width
            items_in_current_row += 1

        final_field_y = self.generator.current_y - checkbox_size - 12

        if self.generator.current_group is not None:
            self._handle_group_positioning(field_x, field_width, final_field_y, starting_y)
        else:
            self.generator.current_y = final_field_y - 5

    # ---------- layout helpers ----------

    def _get_field_position(self):
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
