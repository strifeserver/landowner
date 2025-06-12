from datetime import date


def get_standard_filters(filter_entries, date_check_vars):
    filters = {}

    for col, entry in filter_entries.items():
        val = entry.get().strip()
        if col in ["created_at", "updated_at"]:
            if date_check_vars[col].get() and val:
                filters[col] = val
        else:
            if val:
                filters[col] = val.lower()
    return filters


def get_range_filters(enable_range_var, created_at_from, created_at_to):
    filters = {}

    if enable_range_var.get():
        from_val = created_at_from.get().strip()
        to_val = created_at_to.get().strip()
        if from_val:
            filters["created_at_from"] = from_val
        if to_val:
            filters["created_at_to"] = to_val

    return filters


def apply_filters(
    original_data, filters, date_fields=("created_at", "updated_at")
):
    def matches(row):
        for col, val in filters.items():
            if col in ["created_at_from", "created_at_to"]:
                continue  # Skip range fields for now

            if col in date_fields:
                row_val = str(row.get(col, ""))
            else:
                row_val = str(row.get(col, "")).lower()

            if val not in row_val:
                return False
        return True

    return [row for row in original_data if matches(row)]


def toggle_date_range_inputs(state_var, from_entry, to_entry):
    if state_var.get():
        from_entry.config(state="normal")
        to_entry.config(state="normal")
        from_entry.set_date(date.today())
        to_entry.set_date(date.today())
    else:
        from_entry.config(state="disabled")
        to_entry.config(state="disabled")
        from_entry.delete(0, "end")
        to_entry.delete(0, "end")
