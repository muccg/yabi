from django import template
register = template.Library()


class PyNode(template.Node):
    def __init__(self, code):
        self.code = code

    def render(self, context):
        return eval(self.code, context)

@register.tag(name='py')
def do_code(parser, token):
    code = token[2:]  # skip "py"
    return PyNode(code)


