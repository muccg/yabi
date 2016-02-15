# -*- coding: utf-8 -*-
import urlparse
import httplib2
from cookies import CookieJar, FileCookiePersister
import os
from request import GetRequest, PostRequest

#httplib2.debuglevel = 1

class UnauthorizedError(StandardError):
    pass

class ConnectionError(StandardError):
    pass

DEFAULT_WORKDIR = '.httplib2_workdir'

class Http(object):
    def __init__(self, workdir=DEFAULT_WORKDIR, base_url='', cache=True, cookie_persister=None, disable_ssl_certificate_validation=True):
        self.workdir = workdir
        if cache:
            cache_dir = self.setup_cachedir()
            if disable_ssl_certificate_validation:
                self.h = httplib2.Http(cache_dir, disable_ssl_certificate_validation=True)
            else:
                self.h = httplib2.Http(cache_dir)
        else:
            if disable_ssl_certificate_validation:
                self.h = httplib2.Http(disable_ssl_certificate_validation=True)
            else:
                self.h = httplib2.Http()

        if cookie_persister is None:
            jar_file = os.path.join(self.workdir, 'cookies.txt')
            self.cookie_jar = CookieJar(persister=FileCookiePersister(jar_file))
        else:
            self.cookie_jar = CookieJar(persister=cookie_persister)

        self.base_url = base_url
        if not self.base_url.endswith('/'):
            self.base_url += '/'

    def __enter__(self):
        return self

    def __exit__(self, typ, value, traceback):
        self.finish_session()

    def setup_cachedir(self):
        cachedir = os.path.join(self.workdir, 'cache')
        if not os.path.exists(cachedir):
            os.makedirs(cachedir)
        return cachedir

    def is_relative(self, url):
        pr = urlparse.urlparse(url)
        return pr[0] == '' # empty scheme

    def make_request(self, request):
        req_url = request.url
        if self.is_relative(req_url):
            req_url = self.base_url + req_url
        request.add_headers(self.cookie_jar.cookies_to_send_header(req_url))

        try:
            resp, content = self.h.request(req_url, request.method, body=request.body, headers=request.headers)
        except AttributeError, ae:
            # http://code.google.com/p/httplib2/issues/detail?id=96
            # check that this says "'NoneType' object has no attribute 'makefile'"
            if "'NoneType' object has no attribute 'makefile'" in str(ae):
                raise ConnectionError("Cannot connect to %s"%self.base_url)
            
            raise

        # TODO more error handling required here

        if resp.status == 401:
            raise UnauthorizedError()

        self.cookie_jar.update_from_response(resp, req_url)

        return resp, content

    def finish_session(self):
        self.cookie_jar.save()
