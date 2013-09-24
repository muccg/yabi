from django.template import Library

register = Library()

@register.filter
def lookup(d, index):
    return d[index]
