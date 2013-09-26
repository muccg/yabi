from django.template import Library

register = Library()

@register.filter
def as_sorted(arg):
    return sorted(arg)
