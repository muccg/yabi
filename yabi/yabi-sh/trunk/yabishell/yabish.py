from argparse import ArgumentParser
from collections import namedtuple
import json
import os
import readline
import sys
import uuid

from urllib import quote
from yaphc import Http, UnauthorizedError, PostRequest, GetRequest
from yabishell import errors
from yabishell import actions
from yabishell.utils import human_readable_size

# TODO config file
#YABI_DEFAULT_URL = 'https://faramir/yabife/snapshot/'
YABI_DEFAULT_URL = 'https://ccg.murdoch.edu.au/yabi/'
#YABI_DEFAULT_URL = 'https://ccg.murdoch.edu.au/yabi/'

def main():
    debug = False
    yabi = None
    stagein = None
    try:
        argparser = ArgumentParser(description='YABI shell', add_help=False)
        argparser.add_argument("--yabi-debug", action='store_true', help="Run in debug mode")
        argparser.add_argument("--yabi-bg", action='store_true', help="Run in background")
        argparser.add_argument("--yabi-url", help="The URL of the YABI server", default=YABI_DEFAULT_URL)
        options, args = argparser.parse_known_args()        

        args = CommandLineArguments(args)

        if args.no_arguments or args.first_argument in ('-h', '--help'):
            print_usage()
            return

        if args.first_argument in ('-v', '--version'):
            print_version()
            return

        debug = options.yabi_debug
        yabi = Yabi(url=options.yabi_url, bg=options.yabi_bg, debug=options.yabi_debug)
        action = yabi.choose_action(args.first_argument)
        if action.stagein_required():
            stagein = StageIn(yabi, args)
            files_uris = stagein.do()
            if files_uris:
                args.substitute_file_urls(files_uris)
        action.process(args.rest_of_arguments)
        if stagein:
            stagein.delete_stageindir()

    except Exception, e:
        print_error(e, debug)
    finally:
        if yabi is not None:
            yabi.session_finished()

class StageIn(object):
    def __init__(self, yabi, args):
        self.yabi = yabi
        self.args = args
        self.stageindir = None
        self.files = None
   
    @property
    def debug(self):
        return self.yabi.debug
 
    def do(self):
        if not self.args.local_files:
            return
        self.files = self.files_to_stagein()       
        if not self.files:
            return
 
        files_to_uris = {}
        alldirs, allfiles, total_size = self.collect_files()
        stagein_dir, dir_uris = self.create_stagein_dir(alldirs)
        print "Staging in %s in %i directories and %i files." % (
                human_readable_size(total_size), len(alldirs), len(allfiles))
        files_to_uris.update(dir_uris)
        for f in allfiles:
            rel_path, fname = os.path.split(f.relpath)
            file_uri = self.stagein_file(f, stagein_dir + rel_path)
            files_to_uris[f.relpath] = file_uri
        print "Staging in finished."
        return files_to_uris

    def collect_files(self):
        allfiles = []
        alldirs = []
        total_size = 0
        RelativeFile = namedtuple('RelativeFile', 'relpath fullpath')
        for f in self.files:
            if os.path.isfile(f):
                allfiles.append(RelativeFile(os.path.basename(f), f))
                total_size += os.path.getsize(f)
            if os.path.isdir(f):
                path, dirname = os.path.split(f)
                alldirs.append(RelativeFile(dirname, f))
                for root, dirs, files in os.walk(f):
                    for adir in dirs:
                        dpath = os.path.join(root, adir)
                        rel_dir = dpath[len(f)-1:] 
                        alldirs.append(RelativeFile(rel_dir, dpath))
                    for afile in files:
                        fpath = os.path.join(root, afile)
                        rpath = fpath[len(f)-1:]
                        allfiles.append(RelativeFile(rpath, fpath))
                        total_size += os.path.getsize(fpath)
        return alldirs, allfiles, total_size

    def files_to_stagein(self):
        uri = 'ws/yabish/is_stagein_required'
        params = {'name': self.args.first_argument}
        for i,a in enumerate(self.args.rest_of_arguments):
            params['arg%i' % i] = a
        resp, json_response = self.yabi.post(uri, params)
        response = json.loads(json_response)
        if not response.get('stagein_required'):
            return []
        local_files = self.args.local_files
        return filter(lambda f: f in local_files, response['files'])

    def create_stagein_dir(self, dir_structure):
        uri = 'ws/yabish/createstageindir'
        params = {'uuid': uuid.uuid1()}
        for i,d in enumerate(dir_structure):
            params['dir_%i' % i] = d.relpath
        resp, json_response = self.yabi.post(uri, params)
        response = json.loads(json_response)
        if not response.get('success'):
            raise errors.RemoteError(
                "Couldn't create stagein directory on the server (%s)" % response.get('msg')) 
        stageindir_uri = response['uri']
        dir_uri_mapping = {}
        for d in dir_structure:
            dir_uri = stageindir_uri + d.relpath
            if not dir_uri.endswith('/'):
                dir_uri += '/'
            dir_uri_mapping[d.relpath] = dir_uri
        return stageindir_uri, dir_uri_mapping

    def stagein_file(self, f, stagein_dir):
        uri = 'ws/fs/put?uri=%s' % quote(stagein_dir)
        fname = os.path.basename(f.relpath)
        finfo = (fname, fname, f.fullpath)
        params = {}
        print '  Staging in file: %s (%s).' % (
                f.relpath,human_readable_size(os.path.getsize(f.fullpath)))
        resp, json_response = self.yabi.post(uri, params, files=[finfo])
        assert resp.status == 200
        return os.path.join(stagein_dir, fname)

    def delete_stageindir(self):
        if self.stageindir:
            self.yabi.delete_dir(self.stageindir)

class Yabi(object):
    def __init__(self, url, bg=False, debug=False):
        self._http = None
        self.yabi_url = url
        self.workdir = os.path.expanduser('~/.yabish')
        self.cachedir = os.path.join(self.workdir, 'cache')
        self.cookiesfile = os.path.join(self.workdir, 'cookies.txt')
        self.username = None
        self.run_in_background = bg
        self.debug = debug
        if self.debug:
            import httplib2
            httplib2.debuglevel = 1

    @property
    def http(self):
        if self._http is None:
            self._http = Http(workdir=self.workdir, base_url=self.yabi_url)
        return self._http

    def delete_dir(self, stageindir):
        rmdir = actions.Rm(self)
        rmdir.process([stageindir])

    def login(self):
        import getpass
        system_user = getpass.getuser()
        username = raw_input('Username (%s): ' % system_user)
        if '' == username.strip():
            username = system_user
        password = getpass.getpass()
        login_action = actions.Login(self)
        return login_action.process([username, password])

    def request(self, method, url, params=None, files=None):
        if params is None:
            params = {}
        act_as_ajax = {'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest'}
        try:
            if method == 'GET':
                request = GetRequest(url, params, headers=act_as_ajax)
            elif method == 'POST':
                request = PostRequest(url, params, files=files, headers=act_as_ajax)
            else:
                assert False, "Method should be GET or POST"
            if self.debug:
                print '=' * 5 + 'Making HTTP request'
            resp, contents = self.http.make_request(request)
            if self.debug:
                print resp, contents
                print '=' * 5 + 'End of HTTP request'
        except UnauthorizedError:
            if not self.login():
                raise StandardError("Invalid username/password")
            resp, contents = self.http.make_request(request)
        if int(resp.status) >= 400:
            raise errors.CommunicationError(int(resp.status), url, contents)
        return resp, contents

    def get(self, url, params=None):
        return self.request('GET', url, params)

    def post(self, url, params=None, files=None):
        return self.request('POST', url, params=params, files=files)

    def choose_action(self, action_name):
        class_name = action_name.capitalize()
        try:
            cls = getattr(sys.modules['yabishell.actions'], class_name)
        except AttributeError:
            if self.run_in_background:
                cls = actions.BackgroundRemoteAction
            else:
                cls = actions.ForegroundRemoteAction
        return cls(self, name=action_name)

    def session_finished(self):
        if self._http:
            self._http.finish_session()

def print_usage():
    print '''
Welcome to Yabish!

Command should be used like BLA BLA BLA
'''

def print_version():
    from version import __version__ 
    print 'yabish %s' % __version__

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

    @property
    def all_arguments(self):
        return self.args

    @property
    def local_files(self):
        return filter(lambda arg: os.path.isfile(arg) or os.path.isdir(arg), self.args)

    def substitute_file_urls(self, urls):
        def file_to_url(arg):
            new_arg = arg
            if os.path.isfile(arg) or os.path.isdir(arg):
                new_arg = urls.get(os.path.basename(arg), arg)
            return new_arg 
        self.args = map(file_to_url, self.args)

