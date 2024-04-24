from django import template
from datetime import datetime
register = template.Library()

@register.filter(name='split')
def split(value, arg):
    print(arg, value)
    return value.split(arg)

@register.filter(name='date')
def date(value):
    return value.strftime("%Y-%m-%d" )
