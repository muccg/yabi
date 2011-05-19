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
class Rule(object):
    """
    A base rule within a ruleset. At this level, the only attributes a rule can
    have are a name and an optional sanitiser.
    """

    def __init__(self, ruleset, name):
        """Constructs a Rule object."""

        self.name = name
        self.ruleset = ruleset
        self.sanitiser = None

    def sanitise(self, value):
        """
        Sanitises the given value according to the sanitiser set within the
        rule. If no sanitiser is set, the value is returned unchanged.
        """

        if self.sanitiser:
            return self.ruleset.sanitise(self.sanitiser, value)
        return value

    def set_sanitiser(self, name):
        """
        Sets the sanitiser used within the rule. The name is expected to be the
        name of a sanitiser set within the parent ruleset.
        """

        self.sanitiser = name


class Ruleset(object):
    """
    A set of sanitisation and whitelisting rules to be applied to a document
    (whether HTML, CSS, or other) being previewed.

    This will need to be extended for the specific type of ruleset being
    represented, as each ruleset type will have its own rule parsing semantics.

    By default, the elements within the ruleset are exposed via a dict-like
    interface.
    """

    def __init__(self, elements):
        """Constructs a new ruleset."""

        self.elements = {}
        self.sanitisers = {}

        self.parse(elements)

    def __contains__(self, key):
        return key in self.elements

    def __delitem__(self, key):
        del(self.elements[key])

    def __getitem__(self, key):
        return self.elements[key]

    def __setitem__(self, key, value):
        self.elements[key] = value

    def add_sanitiser(self, name, func):
        """Registers a sanitisation function for the ruleset."""

        self.sanitisers[name] = func

    def get_sanitiser(self, name):
        return self.sanitisers[name]

    def parse(self, elements):
        """
        Parses the given set of elements in whatever form the ruleset expects.
        Not implemented in this base class.
        """

        raise NotImplemented

    def sanitise(self, name, value):
        """
        Sanitises the given value with the requested sanitisation function. If
        the requested sanitisation function isn't registered with this ruleset,
        a KeyError will be thrown.
        """

        return self.sanitisers[name](value)
