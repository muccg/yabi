from django.core.cache import cache
from pickle import Pickler, Unpickler

from cookies import Cookie

class DjangoCacheCookiePersister(object):
    def __init__(self, key, cache_time=30*60):
        self.key = str(key)
        self.cache_time = cache_time

    def save(self, cookies):
        raw_cookies = '' 
        for cookie in [c for c in cookies if not c.is_session_cookie]:
            raw_cookies += cookie.as_str + '\n'
        cache.set(self.key, raw_cookies, self.cache_time)

    def load(self):
        cookies = []
        raw_cookies = cache.get(self.key)
        if raw_cookies:
            for l in [l.strip() for l in raw_cookies.split('\n') if l.strip() != '']:
                cookies.append(Cookie.from_str(l)) 
        return cookies

