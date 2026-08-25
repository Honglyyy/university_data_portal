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
@register.filter
def grade_badge_class(grade):
    if not grade:
        return 'bg-secondary bg-opacity-10 text-secondary'
    grade = str(grade).upper()
    if grade.startswith('A'):
        return 'bg-success bg-opacity-10 text-success'
    elif grade.startswith('B'):
        return 'bg-primary bg-opacity-10 text-primary'
    elif grade.startswith('C'):
        return 'bg-info bg-opacity-10 text-info'
    elif grade.startswith('D'):
        return 'bg-warning bg-opacity-10 text-warning'
    elif grade.startswith('E'):
        return 'bg-secondary bg-opacity-10 text-secondary'
    elif grade.startswith('F'):
        return 'bg-danger bg-opacity-10 text-danger'
    return 'bg-secondary bg-opacity-10 text-secondary'
