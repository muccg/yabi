import time, calendar
from urlparse import urlparse
import re
import os

class CookieParser(object):
    def cookie_defaults(self, request_url):
        url = urlparse(request_url)
        domain = url.hostname
        path = '/'
        rightmost_slash = url.path.rfind('/')
        if rightmost_slash != -1:
            path = url.path[:rightmost_slash+1]
        return (domain, path)

    def split_cookies(self, header_value):
        # all commas before a name=value pair. Doesn't match commas in values
        pattern = ',[^;]+='
        start_indexes, end_indexes = [0], []
        for m in re.finditer(pattern, header_value):
            end_indexes.append(m.start())
            start_indexes.append(m.start()+1)
        end_indexes.append(len(header_value))
        return [header_value[start:end].strip()
                    for start,end in zip(start_indexes, end_indexes)]

    def parse_cookie(self, raw_cookie, default_domain, default_path):
        if not raw_cookie:
            return None
        values = raw_cookie.split(';')
        domain, path = default_domain, default_path
        secure = False
        expires_on = None
        first_pair = values[0]
        cookie_name,cookie_value = first_pair.split('=')
        for name, value in [(v[0].strip(),v[1].strip()) for v in [v.split('=')+[''] for v in values[1:]]]:
            if 'secure' == name:
                secure = True
            if 'expires' == name:
                expires_on = time.strptime(value, '%a, %d-%b-%Y %H:%M:%S %Z')       
            # TODO potentially these could be sanity checked against request URL
            # as per spec, but we probably can trust YABI
            if 'domain' == name:
                domain = value
                if not domain.startswith('.'):
                    domain = '.' + domain
            if 'path' == name:
                path = value
        return Cookie(cookie_name, cookie_value, domain, path, expires_on, secure)

    def write_header_value(self, cookies):
        return "; ".join(["%s=%s" % (c.name,c.value) for c in cookies])

    def parse_header(self, header, request_url):
        default_domain, default_path = self.cookie_defaults(request_url)
        return [self.parse_cookie(cookie,default_domain, default_path) 
                    for cookie in self.split_cookies(header)]

class CookieJar(object):
    def __init__(self, cookies = None, jar_file=None):
        self.parser = CookieParser()
        self._cookies = []
        self.jar_file = jar_file
        if self.jar_file is not None:
            self.load_from_file()
        if cookies:
            self._cookies.extend(cookies)

    @property
    def empty(self):
        return len(self._cookies) == 0

    def find_cookie(self, cookie):
        for i, c in enumerate(self._cookies):
            if c.is_older_version_of(cookie):
                return i
        return -1

    def add_cookies(self, cookies):
        for cookie in cookies:
            cookie_pos = self.find_cookie(cookie)
            if cookie_pos != -1:
                self._cookies[cookie_pos] = cookie
            else:
                self._cookies.append(cookie)

    def update_from_response(self, response, request_url):
        cookie_header = response.get('set-cookie')
        if not cookie_header:
            return
        cookies = self.parser.parse_header(cookie_header, request_url)
        self.add_cookies(cookies)

    def should_send_cookie(self, cookie, scheme, domain, path):
        return (
            cookie.matches_domain(domain) and
            path.startswith(cookie.path) and
            (not cookie.is_secure or scheme=='https') and
            (cookie.is_session_cookie or cookie.expires_on >= time.gmtime())
        )

    def cookies_to_send_header(self, request_url):
        cookies = self.cookies_to_send(request_url)
        if not cookies:
            return {}
        return { "Cookie": self.parser.write_header_value(cookies) }

    def cookies_to_send(self, request_url):
        url = urlparse(request_url)
        domain = url.hostname
        def most_specific_paths_first(cookie1, cookie2): 
            return cmp(cookie2.path, cookie1.path)
        return sorted(
            [cookie for cookie in self._cookies 
                if self.should_send_cookie(cookie, url.scheme, domain, url.path)],
            cmp = most_specific_paths_first
        )

    @property
    def cookies(self):
        return tuple(self._cookies)

    def save_to_file(self):
        with open(self.jar_file, 'w') as f:
            for cookie in [c for c in self._cookies if not c.is_session_cookie]:
                f.write(cookie.as_str + "\n")

    def load_from_file(self):
        if not os.path.isfile(self.jar_file):
            return
        with open(self.jar_file, 'r') as f:
            for l in [l.strip() for l in f if l.strip() != '']:
                self._cookies.append(Cookie.from_str(l))

class Cookie(object):
    def __init__(self, name, value, domain, path, expires_on=None, secure=False):
        self.name, self.value = name, value
        self.domain = domain
        self.path = path
        self.is_secure = secure
        self.expires_on = expires_on        

    @staticmethod
    def from_str(s):
        # TODO clean this up
        args = s.split(';')
        args[4] = time.gmtime(float(args[4]))
        return Cookie(*args)

    @property
    def is_session_cookie(self):
        return (self.expires_on is None)

    def matches_domain(self, domain):
        return (
            self.domain == domain or
            (self.domain.startswith('.') and domain.endswith(self.domain))
        )

    def is_older_version_of(self, cookie):
        '''Is the passed in cookie an updated version of this cookie'''
        return (self.name == cookie.name and self.domain == cookie.domain
                and self.path == self.path)

    @property
    def as_str(self):
        return ";".join([str(v) for v in [self.name, self.value, self.domain, self.path, calendar.timegm(self.expires_on), self.is_secure]])

