from django import template
register = template.Library()


class SimpleImportNode(template.Node):
    def __init__(self, module_name):
        self.module_name = module_name

    def render(self, context):
        # side-effect on  context
        context_dict = context.dicts[-1]
        context_dict.update({self.module_name: __import__(self.module_name)})
        return ""


@register.tag(name='import')
def do_import(parser, token):
    """
    @param parser:
    @param token:
    @return: SimpleImportNode

    E.g.  {% import foobar %} - Adds foobar to context so subsequent {% py foobar.baz() %} calls work

    """
    parts = token.split_contents()
    module_name = parts[1]
    return SimpleImportNode(module_name)


