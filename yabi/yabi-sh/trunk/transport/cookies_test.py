from unittest import TestCase
from cookies import Cookie, CookieJar, CookieParser
import time
import tempfile

class CookieAssert(object):
     def assertCookie(self, cookie, name, value, domain, path, secure, session, expires_on=None):
        self.assertEqual(cookie.name, name)
        self.assertEqual(cookie.value, value)
        self.assertEqual(cookie.domain, domain)
        self.assertEqual(cookie.path, path)
        self.assertEqual(cookie.is_secure, secure)
        self.assertEqual(cookie.is_session_cookie, session)
        if expires_on is None:
            self.assertTrue(cookie.expires_on is None)
        else:
            self.assertEqual(cookie.expires_on, time.strptime(expires_on, '%d-%m-%Y %H:%M:%S %Z'))

class CookieParserTest(TestCase, CookieAssert):
    def setUp(self):
        self.parser = CookieParser()

    def test_parse_simple_defaults_from_request_url(self):
        cookie_header = 'mycookie=myvalue'
        request_url = 'https://some.domain.com:1234/some/path?some=query'

        cookie_list = self.parser.parse_header(cookie_header, request_url)

        self.assertEqual(len(cookie_list), 1)
        self.assertCookie(cookie_list[0], name='mycookie', value='myvalue', 
            domain='some.domain.com', path='/some/', secure=False, session=True)

    def test_parse_full(self):
        cookie_header = 'mycookie=myvalue; expires= Thu, 1-Jul-2010 12:13:14 GMT; domain =some.other.domain.com; path=/some/other/path/; secure'
        request_url = 'https://some.domain.com:1234/some/path?some=query'

        cookie_list = self.parser.parse_header(cookie_header, request_url)

        self.assertEqual(len(cookie_list), 1)
        self.assertCookie(cookie_list[0], name='mycookie', value='myvalue', 
            domain='.some.other.domain.com', path='/some/other/path/', 
            secure=True, session=False, expires_on='01-07-2010 12:13:14 GMT')

    def test_parse_three_cookies(self):
        cookie_header = 'mycookie=myvalue; expires= Thu, 1-Jul-2010 12:13:14 GMT; domain =some.other.domain.com; path=/some/other/path/; secure, mysecondcookie=othervalue; expires= Fri, 2-Jul-2010 13:14:15 GMT; domain=some.other.domain; path=/some/,thirdcookie=value'
        request_url = 'https://some.domain.com:1234/some/path?some=query'

        cookie_list = self.parser.parse_header(cookie_header, request_url)

        self.assertEqual(len(cookie_list), 3)
        cookie1, cookie2, cookie3 = cookie_list
        self.assertEqual(cookie1.name, 'mycookie')
        self.assertEqual(cookie1.value, 'myvalue')
        self.assertEqual(cookie2.name, 'mysecondcookie')
        self.assertEqual(cookie2.value, 'othervalue')
        self.assertEqual(cookie3.name, 'thirdcookie')
        self.assertEqual(cookie3.value, 'value')


class EmptyCookieJarTest(TestCase):

    def setUp(self):
        self.jar = CookieJar()

    def test_cookie_jar_empty(self):
        self.assertTrue(self.jar.empty)

    def test_update_from_response(self):
        response = {
            'set-cookie': 'mycookie=myvalue'
        }
        request_url = 'https://some.domain.com:1234/some/path?some=query'
        self.jar.update_from_response(response, request_url)

        cookie_list = self.jar.cookies
        cookie = cookie_list[0]
        self.assertFalse(self.jar.empty)
        self.assertEqual(len(cookie_list), 1)
        self.assertEqual(cookie.name, 'mycookie')
        self.assertEqual(cookie.value, 'myvalue')

    def test_cookies_to_send_no_cookie(self):
        cookie_list = self.jar.cookies_to_send('http://some.domain.com/some/path')
        self.assertEqual(len(cookie_list), 0)

class CookieJarTest(TestCase):
    def setUp(self):
        self.jar = self.build_jar()

    def build_jar(self, name='cookie', value='value', 
              domain='some.domain.com', path='/some/', secure=False, expires_on=None):
        return CookieJar([
            Cookie(name, value, domain, path, secure=secure, expires_on=expires_on),
        ])

    def test_cookies_to_send_everything_matches(self):
        cookie_list = self.jar.cookies_to_send('http://some.domain.com/some/path')
        self.assertEqual(len(cookie_list), 1)
        cookie = cookie_list[0]
        self.assertEquals(cookie.name, 'cookie')
        self.assertEquals(cookie.value, 'value')

    def test_cookies_to_send_other_domain(self):
        cookie_list = self.jar.cookies_to_send('http://other.domain.com/some/path')
        self.assertEqual(len(cookie_list), 0)

    def test_cookies_to_send_subdomain_cookie_strict(self):
        cookie_list = self.jar.cookies_to_send('http://subdomain.some.domain.com/some/path')
        self.assertEqual(len(cookie_list), 0)
   
    def test_cookies_to_send_subdomain_cookie_permissive(self):
        jar = self.build_jar(domain='.some.domain.com')
        cookie_list = jar.cookies_to_send('http://subdomain.some.domain.com/some/path')
        self.assertEqual(len(cookie_list), 1)

    def test_cookies_to_send_other_path(self):
        cookie_list = self.jar.cookies_to_send('http://some.domain.com/someother/path')        
        self.assertEqual(len(cookie_list), 0)

    def test_cookies_to_send_root_path(self):
        cookie_list = self.jar.cookies_to_send('http://some.domain.com')        
        self.assertEqual(len(cookie_list), 0)

    def test_cookies_to_send_other_same_level_path(self):
        cookie_list = self.jar.cookies_to_send('http://some.domain.com/some/otherpath')        
        self.assertEqual(len(cookie_list), 1)

    def test_cookies_to_send_secure_only_cookie_https(self):
        jar = self.build_jar(secure=True)
        cookie_list = jar.cookies_to_send('https://some.domain.com/some/path')
        self.assertEqual(len(cookie_list), 1)

    def test_cookies_to_send_secure_only_cookie_http(self):
        jar = self.build_jar(secure=True)
        cookie_list = jar.cookies_to_send('http://some.domain.com/some/path')
        self.assertEqual(len(cookie_list), 0)

    def test_cookies_to_send_cookie_expires_in_future(self):
        future_time = time.gmtime(time.time()+60)
        jar = self.build_jar(expires_on=future_time)
        cookie_list = jar.cookies_to_send('http://some.domain.com/some/path')
        self.assertEqual(len(cookie_list), 1)

    def test_cookies_to_send_cookie_expired(self):
        past_time = time.gmtime(time.time()-1)
        jar = self.build_jar(expires_on=past_time)
        cookie_list = jar.cookies_to_send('http://some.domain.com/some/path')
        self.assertEqual(len(cookie_list), 0)

    def test_update_from_response_changes_existing_cookie(self):
        response = {
            'set-cookie': 'cookie=newvalue'
        }
        request_url = 'http://some.domain.com/some/path'
        self.jar.update_from_response(response, request_url)

        cookie_list = self.jar.cookies
        cookie = cookie_list[0]
        self.assertFalse(self.jar.empty)
        self.assertEqual(len(cookie_list), 1)
        self.assertEqual(cookie.name, 'cookie')
        self.assertEqual(cookie.value, 'newvalue')



class CookieJarWith2CookiesTest(TestCase):
    def setUp(self):
        # TODO func
        future_time = time.gmtime(time.time()+60)
        cookies = [ 
            Cookie(name='cookie', value='value', domain='some.domain.com', 
                    path='/some/', expires_on=future_time),
            Cookie(name='othercookie', value='value', domain='some.domain.com', 
                    path='/some/path/'),
        ]
        self.jar_file = tempfile.mktemp()
        self.jar = CookieJar(cookies, jar_file=self.jar_file)

    def test_cookies_to_send_orders_cookies_properly(self):
        '''More specific paths should come before the rest'''
        cookie_list = self.jar.cookies_to_send('http://some.domain.com/some/path/something')
        self.assertEqual(len(cookie_list), 2)
        self.assertEqual(cookie_list[0].name, 'othercookie')
        self.assertEqual(cookie_list[1].name, 'cookie')

    def test_cookies_to_send_header_no_cookies(self):
        headers_map = self.jar.cookies_to_send_header('http://some.otherdomain.com')
        self.assertEqual(len(headers_map), 0)

    def test_cookies_to_send_header_2_cookies(self):
        headers_map = self.jar.cookies_to_send_header('http://some.domain.com/some/path/something')
        self.assertEqual(len(headers_map), 1)
        self.assertEqual(headers_map['Cookie'], 
            'othercookie=value; cookie=value')

    def test_persistence(self):
        self.jar.save_to_file()
        new_jar = CookieJar(jar_file=self.jar_file)
        self.assertEqual(len(new_jar.cookies), 1)

if __name__ == "__main__":
    unittest.main()
