from django import template
from parking_places.views import get_simple_format_adress

register = template.Library()

@register.filter
def simple_format_title(parking_place):
    return get_simple_format_adress(parking_place)