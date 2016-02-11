import copy
import urllib
from multipart_form_encoder import MultipartFormEncoder


class Request(object): 
    def __init__(self, method, url, params = None, headers = None):
        self.method = method
        self._url = url
        self._params = params
        self._headers = {} if headers is None else headers
        self._body = None

    @property
    def url(self):
        return self._url

    @property
    def headers(self):
        return self._headers

    def add_headers(self, headers):
        self._headers.update(headers)

    @property
    def body(self):
        return self._body

class GetRequest(Request):
    def __init__(self, url, params=None, headers=None):
        Request.__init__(self, 'GET', url, params, headers)

    @property
    def url(self):
        return self._url + '?' + urllib.urlencode(self._params)


class PostRequest(Request):
    def __init__(self, url, params=None, headers=None, files=None):
        Request.__init__(self, 'POST', url, params, headers)
        self._files = files
        self.set_up()

    @property
    def headers(self):
        return copy.copy(self._headers)

    def set_up(self):
        if self._files:
            self._body, headers = self.encode_multipart_form()
        else:
            self._body, headers = self.encode_form()
        self._headers.update(headers)

    def encode_form(self):
        body = urllib.urlencode(self._params) if self._params else None
        headers = {
            "Content-Type":"application/x-www-form-urlencoded",
            "Accept":"text/plain"
        }
        return body, headers

    def encode_multipart_form(self):
        encoder = MultipartFormEncoder()
        body = encoder.encode(tuple(self._params.items()), self._files)
        headers = {
            'Content-Type': encoder.content_type,
            'Content-Length': str(len(body))
        }
        return body, headers


