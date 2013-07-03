from django import template
register = template.Library()


class PyNode(template.Node):
    def __init__(self, code):
        self.code = code

    def render(self, context):
        code_context = {}
        for context_dict in context.dicts:
            code_context.update(context_dict)
        return eval(self.code, code_context)



@register.tag(name='py')
def do_code(parser, token):
    parts = token.split_contents()
    code = " ".join(parts[1:])
    return PyNode(code)


