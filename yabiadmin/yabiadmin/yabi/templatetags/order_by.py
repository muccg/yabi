from django.template import Library

register = Library()

@register.filter
def order_by(generator, order_by_arg):
    new_gen = getattr(generator, "order_by")
    for obj in new_gen(order_by_arg):
        yield obj
