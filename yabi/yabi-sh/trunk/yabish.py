#!/usr/bin/env python

import sys
import readline

from yaphc import Http, UnauthorizedError, PostRequest, GetRequest
import actions

# TODO env variable

DEBUG = True
YABI_URL = 'https://faramir:19443/yabi/'

def main():
    yabi = Yabi()
    try:
        args = CommandLineArguments(sys.argv)

        if args.no_arguments:
            print_usage()
            return
        action = yabi.choose_action(args.first_argument)
        action.process(args.rest_of_arguments)
    except Exception, e:
        print_error(e)
        if DEBUG:
            print '-' * 5 + ' DEBUG ' + '-' * 5
            raise
    finally:
        yabi.session_finished()

class Yabi(object):
    def __init__(self):
        self.http = Http(base_url=YABI_URL)
        self.username = None
       
    def login(self):
        import getpass
        system_user = getpass.getuser()
        username = raw_input('Username (%s): ' % system_user)
        if '' == username.strip():
            username = system_user
        password = getpass.getpass()
        login_url = "login"
        request = PostRequest('login', params= {
            'username': username, 'password': password})
        # TODO change to call web service login and check result
        self.http.make_request(request)
        self.username = username

    def get(self, url, params):
        try:
            request = GetRequest(url, params)
            resp, contents = self.http.make_request(request)
        except UnauthorizedError:
            self.login()
            resp, contents = self.http.make_request(request)
        return resp, contents

    def choose_action(self, action_name):
        class_name = action_name.upper()
        try:
            cls = getattr(sys.modules['actions'], action_name.upper())
        except AttributeError:
            raise StandardError('Unsupported action: ' + action_name)
        return cls(self)

    def session_finished(self):
        self.http.finish_session()

def print_usage():
    print '''
BLA BLA BLA

Command should be used like BLA BLA BLA
'''

def print_error(error):
    print 'An error occured: \n\t%s' % error

class CommandLineArguments(object):
    def __init__(self, argv):
        self.argv = argv

    @property
    def no_arguments(self):
        return len(sys.argv) == 1

    @property
    def first_argument(self):
        return self.argv[1]

    @property
    def rest_of_arguments(self):
        return [] if len(self.argv) <= 2 else self.argv[2:]

if __name__ == "__main__":
    main()

