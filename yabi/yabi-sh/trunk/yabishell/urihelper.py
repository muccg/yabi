from urlparse import urlparse

import re
re_url_schema = re.compile(r'\w+')


def uriparse(uri):
    """
    This function returns a tuple containing the scheme and the ParseResult object.
    It is done this way as urlparse only accepts a specific list of url schemes
    and yabi:// is not one of them. The ParseResult object is read-only so
    we cannot inject the scheme back into it.
    """
    scheme, rest = uri.split(":",1)
    assert re_url_schema.match(scheme)        
    return (scheme, urlparse(rest))
