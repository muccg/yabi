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
