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
from cssutils import css, CSSParser, replaceUrls

import ruleset


class Ruleset(ruleset.Ruleset):
    """A CSS specific ruleset class."""

    def parse(self, properties):
        """Parses a sequence or dict of allowed CSS property names."""

        if isinstance(properties, list) or isinstance(properties, tuple):
            properties = dict(zip(properties, [True] * len(properties)))

        for property, value in properties.iteritems():
            self[property] = value


# A default set of allowable CSS properties, based on the list of properties in
# the CSS 2.1 specification. At present, the only included CSS 3 property is
# the commonly (over-)used "text-shadow", but this may be extended to other
# safe properties as the need arises.
DEFAULT_ALLOWED_PROPERTIES = (
    "background-attachment",
    "background-color",
    "background-image",
    "background-position",
    "background-repeat",
    "background",
    "border-collapse",
    "border-color",
    "border-spacing",
    "border-style",
    "border-top",
    "border-right",
    "border-bottom",
    "border-left",
    "border-top-color",
    "border-right-color",
    "border-bottom-color",
    "border-left-color",
    "border-top-style",
    "border-right-style",
    "border-bottom-style",
    "border-left-style",
    "border-width",
    "border",
    "border-radius",
    "border-radius-top-left",
    "border-radius-top-right",
    "border-radius-bottom-right",
    "border-radius-bottom-left",
    "bottom",
    "caption-side",
    "clear",
    "clip",
    "color",
    "content",
    "counter-increment",
    "counter-reset",
    "cursor",
    "direction",
    "display",
    "empty-cells",
    "float",
    "font-family",
    "font-size",
    "font-style",
    "font-variant",
    "font-weight",
    "font",
    "height",
    "left",
    "letter-spacing",
    "line-height",
    "list-style-image",
    "list-style-position",
    "list-style-type",
    "list-style",
    "margin-right",
    "margin-left",
    "margin-top",
    "margin-bottom",
    "margin",
    "max-height",
    "max-width",
    "min-height",
    "min-width",
    "orphans",
    "outline-color",
    "outline-style",
    "outline-width",
    "outline",
    "overflow",
    "padding-top",
    "padding-right",
    "padding-bottom",
    "padding-left",
    "padding",
    "position",
    "quotes",
    "right",
    "table-layout",
    "text-align",
    "text-decoration",
    "text-indent",
    "text-shadow",
    "text-transform",
    "top",
    "unicode-bidi",
    "vertical-align",
    "visibility",
    "white-space",
    "widows",
    "width",
    "word-spacing",
    "z-index",
)


# Set up some default objects.

# A default fetcher for cssutils that will ensure that no external stylesheets
# included via @import are loaded.
default_fetcher = lambda url: (None, "")

# A default parser that uses the default fetcher.
default_parser = CSSParser(fetcher=default_fetcher)

# The default CSS ruleset.
default_ruleset = Ruleset(DEFAULT_ALLOWED_PROPERTIES)


def _sanitise(content, parser=default_parser, ruleset=default_ruleset):
    """
    The actual implementation of the CSS sanitiser.
    """

    input = parser.parseString(content)
    output = css.CSSStyleSheet()

    def primitive(value):
        # This is the one place where we'll blacklist rather than whitelist:
        # all of the primitive types defined by cssutils are safe except for
        # URIs and "unknowns" (which includes IE's Javascript expression syntax
        # and filter values).
        if value.primitiveType not in (value.CSS_URI, value.CSS_UNKNOWN):
            return value.cssText

        return ""

    def rule(input_rule):
        # Non-style elements are presently stripped. We may want to maintain
        # comments at some point, but for now we'll only pass the barest
        # structural elements that we're sure are safe through.
        if input_rule.type == input_rule.STYLE_RULE:
            output_rule = css.CSSStyleRule(selectorText=input_rule.selectorText, parentStyleSheet=output)

            for prop in input_rule.style:
                if prop.name.lower() in ruleset:
                    output_rule.style.setProperty(prop.name, value(prop.cssValue))

            output.add(output_rule)

    def value(input_value):
        output_value = []

        # Values aren't necessarily inherently primitive to start with: lists
        # of values are also permissible in numerous places within CSS (for
        # example: "border: solid 1px black" is a list of three values), so we
        # need to ensure that we deal with each value independently (since a
        # background definition might include an image that we want to strip,
        # but a colour that we want to keep).
        if isinstance(input_value, css.CSSValueList):
            # CSS value lists can't recurse, so we can assume that the depth
            # will never be more than one, and hence use a simple for loop
            # here.
            for v in input_value:
                if isinstance(v, css.CSSPrimitiveValue):
                    output_value.append(primitive(v))
        elif isinstance(input_value, css.CSSPrimitiveValue):
            output_value.append(primitive(input_value))

        return " ".join(output_value)

    for r in input:
        rule(r)

    return output


def sanitise(content, parser=default_parser, ruleset=default_ruleset):
    """Sanitises the given CSS stylesheet content."""

    return _sanitise(content, parser=parser, ruleset=ruleset).cssText


def sanitise_inline(content, parser=default_parser, ruleset=default_ruleset):
    """Sanitises the given CSS inline style."""

    # Quick, dirty, but effective: the cssutils parser can only parse
    # full-blown stylesheets with selectors, so we'll wrap the inline content
    # in a fake rule and parse that.
    wrapped_content = "_inline_sanitise { " + content + " }"

    sheet = _sanitise(wrapped_content, parser=parser, ruleset=ruleset)

    # Pluck out the rule we actually care about.
    for rule in sheet:
        if rule.type == rule.STYLE_RULE and rule.selectorText == "_inline_sanitise":
            return rule.style.cssText.replace("\n", " ")

    return ""
