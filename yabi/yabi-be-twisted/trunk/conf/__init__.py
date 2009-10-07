
from urlparse import urlparse

# we store the config inside a class
class yabiadmin:
    SERVER = "localhost"
    PORT = 8000
    PATH = "/yabiadmin"

    @classmethod
    def parse_url(cls,url):
        uri = "http://"+url if not urlparse(url).netloc else url
        parse = urlparse(uri)
        print "setting yabiadmin uri to:",parse
        cls.SERVER = parse.hostname
        cls.PORT = parse.port
        cls.PATH = parse.path
    