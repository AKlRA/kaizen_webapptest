from django import template

register = template.Library()

@register.filter(is_safe=True)
def split(value, delimiter=','):
    """Returns the string split by delimiter"""
    if value:
        return value.split(delimiter)
    return []

@register.filter
def get_attr(obj, attr):
    """Gets an attribute from an object safely"""
    try:
        return getattr(obj, str(attr), '')
    except (AttributeError, TypeError):
        return ''

@register.filter
def add(value, arg):
    """Concatenates value and arg with underscore"""
    return f"{value}_{arg}"

@register.filter
def get_impact(obj, impact):
    """Gets impact boolean value"""
    return getattr(obj, f'impacts_{impact}', False)

@register.filter
def get_impact_data(impact_data, impact_type):
    """Gets impact data dictionary for a specific impact type"""
    if isinstance(impact_data, dict):
        return impact_data.get(impact_type, {})
    return {}

@register.filter
def get_impact_field(obj, field):
    """Gets impact field value directly from object"""
    try:
        return getattr(obj, str(field), '')
    except (AttributeError, TypeError):
        return ''

@register.filter
def financial_year(date):
    """Returns financial year string"""
    year = int(date.strftime('%Y'))
    return f"{year}-{year + 1}"

@register.filter
def get_dict_item(dictionary, key):
    """Safely get item from dictionary"""
    if isinstance(dictionary, dict):
        return dictionary.get(key, {})
    return {}