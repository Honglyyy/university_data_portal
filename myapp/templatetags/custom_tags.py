from django import template

register = template.Library()

@register.filter
def sum_attr(items, attr_name):
    """Return the sum of a numeric attribute for each item in the iterable.
    Usage: {{ objects|sum_attr:"field_name" }}
    """
    total = 0
    for item in items:
        value = getattr(item, attr_name, 0)
        try:
            total += float(value)
        except (TypeError, ValueError):
            continue
    if total.is_integer():
        return int(total)
    return total