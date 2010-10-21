#!/usr/bin/env python

import sys
import readline
import json
from argparse import ArgumentParser

from yaphc import Http, UnauthorizedError, PostRequest, GetRequest
import actions

# TODO config file
YABI_URL = 'https://faramir/yabife/tszabo/'

class CommunicationError(StandardError):
    def __init__(self, status_code, url, response):
        self.status_code = status_code
        self.url = url
        self.response = response

    def __str__(self):
        return "%s - %s" % (self.status_code, self.url)

class RemoteError(StandardError):
    pass

def main():
    debug = False
    yabi = None
    try:
        argparser = ArgumentParser(description='YABI shell', add_help=False)
        argparser.add_argument("--yabi-debug", action='store_true', help="Run in debug mode")
        argparser.add_argument("--yabi-bg", action='store_true', help="Run in background")
        options, args = argparser.parse_known_args()        

        args = CommandLineArguments(args)

        if args.no_arguments or args.first_argument in ('-h', '--help'):
            print_usage()
            return

        yabi = Yabi(bg=options.yabi_bg, debug=options.yabi_debug)
        action = yabi.choose_action(args.first_argument)
        action.process(args.rest_of_arguments)

    except Exception, e:
        print_error(e, debug)
    finally:
        if yabi is not None:
            yabi.session_finished()

class Yabi(object):
    def __init__(self, bg=False, debug=False):
        self.http = Http(base_url=YABI_URL)
        self.username = None
        self.run_in_background = bg
        self.debug = debug
        if self.debug:
            import httplib2
            httplib2.debuglevel = 1
 
    def login(self):
        import getpass
        system_user = getpass.getuser()
        username = raw_input('Username (%s): ' % system_user)
        if '' == username.strip():
            username = system_user
        password = getpass.getpass()
        login_action = actions.Login(self)
        return login_action.process([username, password])

    def request(self, method, url, params=None):
        if params is None:
            params = {}
        try:
            if method == 'GET':
                request = GetRequest(url, params)
            elif method == 'POST':
                request = PostRequest(url, params)
            else:
                assert False, "Method should be GET or POST"
            if self.debug:
                print '=' * 5 + 'Making HTTP request'
            resp, contents = self.http.make_request(request)
            if self.debug:
                print '=' * 5 + 'End of HTTP request'
        except UnauthorizedError:
            if not self.login():
                raise StandardError("Invalid username/password")
            resp, contents = self.http.make_request(request)
        if resp.status >= 400:
            raise CommunicationError(resp.status, url, contents)
        return resp, contents

    def get(self, url, params=None):
        return self.request('GET', url, params)

    def post(self, url, params=None):
        return self.request('POST', url, params)

    def choose_action(self, action_name):
        class_name = action_name.capitalize()
        try:
            cls = getattr(sys.modules['actions'], class_name)
        except AttributeError:
            if self.run_in_background:
                cls = actions.BackgroundRemoteAction
            else:
                cls = actions.ForegroundRemoteAction
        return cls(self, name=action_name)

    def session_finished(self):
        self.http.finish_session()

def print_usage():
    print '''
BLA BLA BLA

Command should be used like BLA BLA BLA
'''

def print_error(error, debug=False):
    print >> sys.stderr, 'An error occured: \n\t%s' % error
    if debug:
        print >> sys.stderr, '-' * 5 + ' DEBUG ' + '-' * 5
        import traceback
        traceback.print_exc()

class CommandLineArguments(object):
    def __init__(self, args):
        self.args = args

    @property
    def no_arguments(self):
        return len(self.args) == 0

    @property
    def first_argument(self):
        return self.args[0]

    @property
    def rest_of_arguments(self):
        return [] if len(self.args) <= 1 else self.args[1:]

if __name__ == "__main__":
    main()

