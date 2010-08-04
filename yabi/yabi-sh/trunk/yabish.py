#!/usr/bin/env python

import sys
import readline

from transport import Transport, UnauthorizedError
import actions

# TODO env variable

DEBUG = True

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
        self.transport = Transport()
        self.username = None
       
    def login(self):
        import getpass
        system_user = getpass.getuser()
        username = raw_input('Username (%s): ' % system_user)
        if '' == username.strip():
            username = system_user
        password = getpass.getpass()
        login_url = "login"
        self.transport.put(login_url, {'username': username, 'password': password})
        self.username = username

    def get(self, url, params):
        try:
            resp = self.transport.get(url, params)
        except UnauthorizedError:
            self.login()
            resp = self.transport.get(url, params)
        return resp
            

    def choose_action(self, action_name):
        class_name = action_name.upper()
        try:
            cls = getattr(sys.modules['actions'], action_name.upper())
        except AttributeError:
            raise StandardError('Unsupported action: ' + action_name)
        return cls(self)

    def session_finished(self):
        self.transport.finish_session()

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

