import memcache
from pickle import Pickler, Unpickler

from cookies import Cookie

class MemcacheCookiePersister(object):
    def __init__(self, servers, key, cache_time=30*60):
        self.servers = servers
        self.key = str(key)
        self.cache_time = cache_time
        self._client = None

    @property
    def client(self):
        if not self._client:
            self._client = memcache.Client(self.servers, debug=0, pickleProtocol=0,
                pickler=Pickler, unpickler=Unpickler, pload=None, pid=None)
        return self._client

    def save(self, cookies):
        raw_cookies = '' 
        for cookie in [c for c in cookies if not c.is_session_cookie]:
            raw_cookies += cookie.as_str + '\n'
        self.client.set(self.key, raw_cookies, self.cache_time, 0)

    def load(self):
        cookies = []
        raw_cookies = self.client.get(self.key)
        if raw_cookies:
            for l in [l.strip() for l in raw_cookies.split('\n') if l.strip() != '']:
                cookies.append(Cookie.from_str(l)) 
        return cookies

