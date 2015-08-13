# Yabi - a sophisticated online research environment for Grid, High Performance and Cloud computing.
# Copyright (C) 2015  Centre for Comparative Genomics, Murdoch University.
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
# 
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


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
