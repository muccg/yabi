import html5lib
import html5lib.sanitizer
import sys


class HTMLSanitizerMixin(html5lib.sanitizer.HTMLSanitizerMixin):
    acceptable_elements = html5lib.sanitizer.HTMLSanitizerMixin.acceptable_elements + ["html", "head", "body"]
    allowed_elements = acceptable_elements + html5lib.sanitizer.HTMLSanitizerMixin.mathml_elements + html5lib.sanitizer.HTMLSanitizerMixin.svg_elements

class HTMLSanitizer(html5lib.tokenizer.HTMLTokenizer, HTMLSanitizerMixin):
    def __init__(self, *args, **kwargs):
        html5lib.tokenizer.HTMLTokenizer.__init__(self, *args, **kwargs)

    def __iter__(self):
        for token in html5lib.tokenizer.HTMLTokenizer.__iter__(self):
            token = self.sanitize_token(token)
            if token:
                yield token


def html(content):
    parser = html5lib.HTMLParser(tree=html5lib.treebuilders.getTreeBuilder("dom"), tokenizer=HTMLSanitizer)
    doc = parser.parse(content)

    walker = html5lib.treewalkers.getTreeWalker("dom")
    stream = walker(doc)

    ser = html5lib.serializer.htmlserializer.HTMLSerializer(omit_optional_tags=False, quote_attr_values=True)
    gen = ser.serialize(stream)

    return u"".join(gen)
