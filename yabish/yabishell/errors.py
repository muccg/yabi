from __future__ import print_function


class CommunicationError(Exception):
    def __init__(self, status_code, url, response):
        self.status_code = status_code
        self.url = url
        self.response = response

    def __str__(self):
        print(self.response)
        return "%s - %s" % (self.status_code, self.url)


class RemoteError(Exception):
    pass
