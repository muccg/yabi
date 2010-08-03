
import sys
import urllib
import httplib2
import readline
from cookies import CookieJar

#httplib2.debuglevel = 1

class UnauthorizedError(StandardError):
    pass

# TODO settings file

YABI_URL = 'https://faramir:19443/yabi/'
JAR_FILE = 'cookies.txt'

class Transport(object):
    def __init__(self):
        self.h = httplib2.Http()
        self.cookie_jar = CookieJar(jar_file=JAR_FILE)
        self.yabi_url = YABI_URL

    # TODO get and put look very similar, extract duplication

    def get(self, url, params={}):
        req_url = self.yabi_url + url
        if params:
            query_string = urllib.urlencode(params)
            req_url = req_url + '?' + query_string
        headers = {}
        headers.update(self.cookie_jar.cookies_to_send_header(req_url))
        resp, content = self.h.request(req_url, headers=headers)

        # Unauthorized
        if resp.status == 401:
            raise UnauthorizedError()

        # TODO raise exceptions if status not 200

        self.cookie_jar.update_from_response(resp, req_url)

        return content

    def put(self, url, params={}):
        req_url = self.yabi_url + url
        body = urllib.urlencode(params)
        headers = {}
        headers.update(self.cookie_jar.cookies_to_send_header(req_url))
        resp, content = self.h.request(req_url, "POST", body=body)

        # Unauthorized
        if resp.status == 401:
            raise UnauthorizedError()

        # TODO raise exceptions if status not 200

        self.cookie_jar.update_from_response(resp, req_url)

        return content

    def finish_session(self):
        self.cookie_jar.save_to_file()

