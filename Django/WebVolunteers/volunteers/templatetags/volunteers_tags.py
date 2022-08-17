from django import template
from . .volunteersLIB import ratingValue
register = template.Library()

@register.filter(name='humman_rating')
def humman_rating(value):
    return ratingValue(value)