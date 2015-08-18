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

from urllib import quote
import logging

from .support import YabiTestCase, StatusResult, all_items, json_path, FileUtils, conf


def remove_slash_if_has(u):
    if u.endswith("/"):
        return u[:-1]
    else:
        return u


try:
    import requests
except ImportError as ioe:
    pass                            # admin imports this file aswell... but doesn't have requests installed :P

class RequestTest(YabiTestCase):
    """This baseclass logs in as the user to perform testing on the yabi frontend"""

    # demo login session
    creds = {'username':conf.yabiusername,'password':conf.yabipassword}

    def setUp(self):
        YabiTestCase.setUp(self)

        self.session = requests.session()

        r = self.session.post(self.yabiurl("login"), data=self.creds)
        self.assertEqual(r.status_code, 200, "Could not login to frontend. Frontend returned: %d"%(r.status_code))

        logging.info("Logged in with: %(username)s/%(password)s" % self.creds)

    @staticmethod
    def yabiurl(path=""):
        "Returns the configured yabi url with `path' appended to it."
        return "%s/%s" % (remove_slash_if_has(conf.yabiurl), path)

    @classmethod
    def fscmd(cls, cmd, uri=None):
        """
        Returns the yabi API url for a fs command, optionally with `uri'
        param in the query string.
        """
        q = "?uri=%s" % quote(uri) if uri is not None else ""
        return cls.yabiurl("ws/fs/%s%s" % (cmd, q))


class RequestTestWithAdmin(RequestTest):
    """This baseclass logs in as the user to perform testing on the yabi frontend"""
    creds = {'username':conf.yabiadminusername,'password':conf.yabiadminpassword}
