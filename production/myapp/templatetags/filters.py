from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key, 0)

@register.filter
def format_decimal(value):
    """Format float to remove .0 for whole numbers and limit to 2 decimals without rounding"""
    if value is None:
        return ""
    try:
        # Convert to float if it's not
        val = float(value)
        if val == int(val):
            return str(int(val))
        else:
            # Truncate to 2 decimal places without rounding
            truncated = int(val * 100) / 100.0
            return f"{truncated:.2f}"
    except (ValueError, TypeError):
        return str(value)


@register.filter
def check_permission(role, module):
    """
    Template filter to check if a role has permission for a module.
    Usage in template: {% if user.role|check_permission:'production' %}
    """
    from myapp.models import RolePermission
    return RolePermission.has_module_access(role, module)
