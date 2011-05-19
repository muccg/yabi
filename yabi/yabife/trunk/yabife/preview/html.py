### BEGIN COPYRIGHT ###
#
# (C) Copyright 2011, Centre for Comparative Genomics, Murdoch University.
# All rights reserved.
#
# This product includes software developed at the Centre for Comparative Genomics 
# (http://ccg.murdoch.edu.au/).
# 
# TO THE EXTENT PERMITTED BY APPLICABLE LAWS, YABI IS PROVIDED TO YOU "AS IS," 
# WITHOUT WARRANTY. THERE IS NO WARRANTY FOR YABI, EITHER EXPRESSED OR IMPLIED, 
# INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND 
# FITNESS FOR A PARTICULAR PURPOSE AND NON-INFRINGEMENT OF THIRD PARTY RIGHTS. 
# THE ENTIRE RISK AS TO THE QUALITY AND PERFORMANCE OF YABI IS WITH YOU.  SHOULD 
# YABI PROVE DEFECTIVE, YOU ASSUME THE COST OF ALL NECESSARY SERVICING, REPAIR
# OR CORRECTION.
# 
# TO THE EXTENT PERMITTED BY APPLICABLE LAWS, OR AS OTHERWISE AGREED TO IN 
# WRITING NO COPYRIGHT HOLDER IN YABI, OR ANY OTHER PARTY WHO MAY MODIFY AND/OR 
# REDISTRIBUTE YABI AS PERMITTED IN WRITING, BE LIABLE TO YOU FOR DAMAGES, INCLUDING 
# ANY GENERAL, SPECIAL, INCIDENTAL OR CONSEQUENTIAL DAMAGES ARISING OUT OF THE 
# USE OR INABILITY TO USE YABI (INCLUDING BUT NOT LIMITED TO LOSS OF DATA OR 
# DATA BEING RENDERED INACCURATE OR LOSSES SUSTAINED BY YOU OR THIRD PARTIES 
# OR A FAILURE OF YABI TO OPERATE WITH ANY OTHER PROGRAMS), EVEN IF SUCH HOLDER 
# OR OTHER PARTY HAS BEEN ADVISED OF THE POSSIBILITY OF SUCH DAMAGES.
# 
### END COPYRIGHT ###
from BeautifulSoup import BeautifulSoup, NavigableString, Tag

import css
import ruleset


class AttributeRule(ruleset.Rule):
    """
    A rule describing an allowable attribute. The only attribute this attribute
    rule can have (confused yet?) is a sanitiser, which ruleset.Rule already
    covers, so there's no extra functionality in this class.
    """

    pass


class ElementRule(ruleset.Rule):
    """
    A rule describing an allowable element and its attributes. The defined
    attributes (expressed as AttributeRule objects) are available via
    dict-style dereferencing.
    """

    def __init__(self, ruleset, name):
        super(ElementRule, self).__init__(ruleset, name)
        self.attributes = {}

    def __contains__(self, name):
        return name in self.attributes

    def __delitem__(self, name):
        del(self.attributes[name])

    def __getitem__(self, name):
        return self.attributes[name]

    def __setitem__(self, name, attr):
        self.attributes[name] = attr

    def add_attribute(self, name, attr):
        """
        Adds the given attribute definition (expressed as a dict) to the
        element by creating and attaching an AttributeRule object.
        """

        attribute = AttributeRule(self.ruleset, name)

        if isinstance(attr, dict) and "sanitiser" in attr:
            attribute.set_sanitiser(attr["sanitiser"])

        self[name] = attribute

    def add_attribute_dict(self, attrs):
        """
        Adds a dict with a set of AttributeRule objects as values. Most useful
        when attaching global attributes to the element's own attributes.
        """

        self.attributes.update(attrs)


class Ruleset(ruleset.Ruleset):
    def parse(self, elements):
        """
        Parses the given dict of elements and attributes (the expected format
        of which is demonstrated by the DEFAULT_ALLOWED_ELEMENTS dict in this
        module) into a ruleset.

        If an element keyed "_global" is defined within the elements, the
        attributes of this element will be applied to all other elements within
        the ruleset.
        """

        self.global_attributes = {}

        try:
            for name, attr in elements["_global"]["attributes"].iteritems():
                rule = AttributeRule(self, name)

                if isinstance(attr, dict) and "sanitiser" in attr:
                    rule.set_sanitiser(attr["sanitiser"])

                self.global_attributes[name] = rule
        except KeyError:
            pass

        for name, options in elements.iteritems():
            if name != "_global":
                self[name] = self.parse_element(name, options)

    def parse_element(self, name, options):
        """Parses an individual element into an ElementRule object."""

        element = ElementRule(self, name)
        element.add_attribute_dict(self.global_attributes)

        if isinstance(options, dict):
            for name, attr in options.get("attributes", {}).iteritems():
                element.add_attribute(name, attr)

            if "sanitiser" in options:
                element.set_sanitiser(options["sanitiser"])

        return element


# Set up the default rule set. Broadly, any defined element or attribute is
# accepted: the value can be True (in which case no sanitisation is performed)
# or a dict with any rule-related definitions (currently, only "sanitiser" is
# understood).
DEFAULT_ALLOWED_ELEMENTS = {
    "a": {
        "attributes": {
            "href": True,
            "rel": True,
            "media": True,
            "hreflang": True,
            "type": True,
        },
    },
    "abbr": True,
    "address": True,
    "area": {
        "attributes": {
            "alt": True,
            "coords": True,
            "shape": True,
            "href": {
                "sanitiser": "url",
            },
            "rel": True,
            "media": True,
            "hreflang": True,
            "type": True,
        },
    },
    "article": True,
    "aside": True,
    "audio": {
        "attributes": {
            "src": {
                "sanitiser": "url",
            },
            "preload": True,
            "autoplay": True,
            "loop": True,
            "controls": True,
        },
    },
    "b": True,
    "base": {
        "attributes": {
            "href": {
                "sanitiser": "url",
            },
        },
    },
    "bdi": True,
    "bdo": True,
    "blockquote": {
        "attributes": {
            "cite": {
                "sanitiser": "url",
            },
        },
    },
    "body": True,
    "br": True,
    "button": {
        "attributes": {
            "disabled": True,
            "form": True,
            "formaction": {
                "sanitiser": "url",
            },
            "formenctype": True,
            "formmethod": True,
            "formnovalidate": True,
            "name": True,
            "type": True,
            "value": True,
        },
    },
    "caption": True,
    "cite": True,
    "code": True,
    "col": {
        "attributes": {
            "span": True,
        },
    },
    "colgroup": {
        "attributes": {
            "span": True,
        },
    },
    "command": {
        "attributes": {
            "type": True,
            "label": True,
            "icon": {
                "sanitiser": "url",
            },
            "disabled": True,
            "checked": True,
            "radiogroup": True,
        },
    },
    "datalist": True,
    "dd": True,
    "del": {
        "attributes": {
            "cite": {
                "sanitiser": "url",
            },
            "datetime": True,
        },
    },
    "details": {
        "attributes": {
            "open": True,
        },
    },
    "dfn": True,
    "div": True,
    "dl": True,
    "dt": True,
    "em": True,
    "fieldset": {
        "attributes": {
            "disabled": True,
            "form": True,
            "name": True,
        },
    },
    "figcaption": True,
    "figure": True,
    "footer": True,
    "form": {
        "attributes": {
            "accept-charset": True,
            "action": {
                "sanitiser": "url",
            },
            "autocomplete": True,
            "enctype": True,
            "method": True,
            "name": True,
            "novalidate": True,
        },
    },
    "h1": True,
    "h2": True,
    "h3": True,
    "h4": True,
    "h5": True,
    "h6": True,
    "head": True,
    "header": True,
    "hgroup": True,
    "hr": True,
    "html": True,
    "i": True,
    "iframe": {
        "attributes": {
            "src": {
                "sanitiser": "url",
            },
            "name": True,
            "sandbox": True,
            "seamless": True,
            "width": True,
            "height": True,
        },
    },
    "img": {
        "attributes": {
            "alt": True,
            "src": {
                "sanitiser": "url",
            },
            "usemap": True,
            "ismap": True,
            "width": True,
            "height": True,
        },
    },
    "input": {
        "attributes": {
            "accept": True,
            "alt": True,
            "autocomplete": True,
            "checked": True,
            "dirname": True,
            "disabled": True,
            "form": True,
            "formaction": {
                "sanitiser": "url",
            },
            "formenctype": True,
            "formmethod": True,
            "formnovalidate": True,
            "height": True,
            "list": True,
            "max": True,
            "maxlength": True,
            "min": True,
            "multiple": True,
            "name": True,
            "pattern": True,
            "placeholder": True,
            "readonly": True,
            "required": True,
            "size": True,
            "src": {
                "sanitiser": "url",
            },
            "step": True,
            "type": True,
            "value": True,
            "width": True,
        },
    },
    "ins": {
        "attributes": {
            "cite": {
                "sanitiser": "url",
            },
            "datetime": True,
        },
    },
    "kbd": True,
    "keygen": {
        "attributes": {
            "challenge": True,
            "disabled": True,
            "form": True,
            "keytype": True,
            "name": True,
        },
    },
    "label": {
        "attributes": {
            "form": True,
            "for": True,
        },
    },
    "legend": True,
    "li": {
        "attributes": {
            "value": True,
        },
    },
    "link": {
        "attributes": {
            "href": {
                "sanitiser": "url",
            },
            "rel": True,
            "media": True,
            "hreflang": True,
            "type": True,
            "sizes": True,
        },
    },
    "map": {
        "attributes": {
            "name": True,
        },
    },
    "mark": True,
    "menu": {
        "attributes": {
            "type": True,
            "label": True,
        },
    },
    "meter": {
        "attributes": {
            "value": True,
            "min": True,
            "max": True,
            "low": True,
            "high": True,
            "optimum": True,
            "form": True,
        },
    },
    "nav": True,
    "noscript": True,
    "ol": {
        "attributes": {
            "reversed": True,
            "start": True,
        },
    },
    "optgroup": {
        "attributes": {
            "disabled": True,
            "label": True,
        },
    },
    "option": {
        "attributes": {
            "disabled": True,
            "label": True,
            "selected": True,
            "value": True,
        },
    },
    "p": True,
    "pre": True,
    "progress": {
        "attributes": {
            "value": True,
            "max": True,
            "form": True,
        },
    },
    "q": {
        "attributes": {
            "cite": {
                "sanitiser": "url",
            },
        },
    },
    "rp": True,
    "rt": True,
    "ruby": True,
    "s": True,
    "samp": True,
    "section": True,
    "select": {
        "attributes": {
            "disabled": True,
            "form": True,
            "multiple": True,
            "name": True,
            "required": True,
            "size": True,
        },
    },
    "small": True,
    "source": {
        "attributes": {
            "src": {
                "sanitiser": "url",
            },
            "type": True,
            "media": True,
        },
    },
    "span": True,
    "strong": True,
    "style": {
        "attributes": {
            "media": True,
            "type": True,
            "scoped": True,
        },
        "sanitiser": "css",
    },
    "sub": True,
    "summary": True,
    "sup": True,
    "table": {
        "attributes": {
            "border": True,
            "summary": True,
        },
    },
    "tbody": True,
    "td": {
        "attributes": {
            "colspan": True,
            "rowspan": True,
            "headers": True,
        },
    },
    "textarea": {
        "attributes": {
            "cols": True,
            "disabled": True,
            "form": True,
            "maxlength": True,
            "name": True,
            "placeholder": True,
            "readonly": True,
            "required": True,
            "rows": True,
            "wrap": True,
        },
    },
    "tfoot": True,
    "th": {
        "attributes": {
            "colspan": True,
            "rowspan": True,
            "headers": True,
            "scope": True,
        },
    },
    "thead": True,
    "time": {
        "attributes": {
            "datetime": True,
            "pubdate": True,
        },
    },
    "title": True,
    "tr": True,
    "track": {
        "attributes": {
            "kind": True,
            "label": True,
            "src": {
                "sanitiser": "url",
            },
            "srclang": True,
        },
    },
    "ul": True,
    "var": True,
    "video": {
        "attributes": {
            "src": {
                "sanitiser": "url",
            },
            "poster": {
                "sanitiser": "url",
            },
            "preload": True,
            "autoplay": True,
            "loop": True,
            "controls": True,
            "width": True,
            "height": True,
        },
    },
    "wbr": True,
    "_global": {
        "attributes": {
            "accesskey": True,
            "class": True,
            "dir": True,
            "hidden": True,
            "id": True,
            "lang": True,
            "style": {
                "sanitiser": "inline_css",
            },
            "tabindex": True,
            "title": True,
        },
    },
}


# Set up a default ruleset based on DEFAULT_ALLOWED_ELEMENTS.
default_ruleset = Ruleset(DEFAULT_ALLOWED_ELEMENTS)

# Add default sanitisers.
default_ruleset.add_sanitiser("css", css.sanitise)
default_ruleset.add_sanitiser("inline_css", css.sanitise_inline)

# The default URL sanitiser strips all URLs; this may be tweaked later to allow
# certain data: URLs based on their MIME type.
default_ruleset.add_sanitiser("url", lambda url: None)


def sanitise(content, ruleset=default_ruleset):
    """
    Sanitise the given (X)HTML content based on the given ruleset. Returns a
    string with the sanitised (X)HTML.
    """

    input = BeautifulSoup(content)
    output = BeautifulSoup()

    context = {}

    def attribute(name, value):
        if name in context["rule"]:
            rule = context["rule"][name]
            value = rule.sanitise(value)

            # Returning None from a sanitiser will result in the attribute
            # simply being ignored.
            if value is not None:
                context["node"][name] = value

    def node(n):
        # Handle a node within the DOM tree appropriately. At present, all
        # non-strings and non-tags are ignored.
        if isinstance(n, NavigableString):
            string(n)
        elif isinstance(n, Tag):
            tag(n)

    def string(ns):
        # Sanitise the string, if the rule requires it.
        value = context["rule"].sanitise(unicode(ns))

        # Returning None from a sanitiser will result in the string not being
        # appended at all.
        if value is not None:
            context["node"].append(value)

    def tag(tag):
        if tag.name in ruleset:
            # Save the previous context for when we pop back up the call stack.
            previous_node = context["node"]
            previous_rule = context["rule"]

            context["node"] = Tag(output, tag.name)
            context["rule"] = ruleset[tag.name]

            # Iterate over the tag's attributes, if any.
            for attr, value in tag.attrs:
                attribute(attr, value)

            # Ditto for the children.
            for child in tag.contents:
                node(child)

            previous_node.append(context["node"])

            # Pop the context before returning.
            context["node"] = previous_node
            context["rule"] = previous_rule

    # Set up the initial context used when walking the tree.
    context["node"] = output
    context["rule"] = ElementRule(ruleset, "toplevel")

    for child in input.contents:
        node(child)

    return output.prettify()
