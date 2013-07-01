from django import template
register = template.Library()


class PyNode(template.Node):
    def __init__(self, code):
        self.code = code

    def render(self, context):
        dict_index = len(context.dicts) - 1
        try:
            result = eval(self.code, context.dicts[dict_index])
            return result
        # Inline with Django Filter behaviour
        except NameError:
            return ""
        except AttributeError:
            return ""
        except Exception, ex:
            raise ex


@register.tag(name='py')
def do_code(parser, token):
    parts = token.split_contents()
    code = " ".join(parts[1:])
    return PyNode(code)


