import time
import json
import os
import sys
import uuid
import urlparse
import errno
import itertools

from yabishell import errors

class Action(object):
    def __init__(self, yabi, name=None):
        self.yabi = yabi
        self.name = name
        if self.name is None:
            self.name = self.__class__.__name__.lower()

    def process(self, args):
        params = self.map_args(args)
        resp, json_response = self.yabi.get(self.url, params)
        return self.process_response(self.decode_json(json_response))

    def decode_json(self, resp):
        return json.loads(resp)        

class FileDownload(object):
    '''Mix into an Action that requires downloading files'''
    get_url = 'ws/fs/get'

    def download_file(self, uri, dest, ignore_404=False):
        params = {'uri': uri}
        try:
            response, contents = self.yabi.get(self.get_url, params)
            if hasattr(dest, 'write'):
                dest.write(contents)
            else:
                with open(dest, 'w') as f:
                    f.write(contents)
        except errors.CommunicationError, e:
            if e.status_code == 404:
                if ignore_404:
                   return
                else:
                   raise errors.RemoteError("File % doesn't exist." % uri)
            else:
                raise

class RemoteAction(Action):
    def __init__(self, *args, **kwargs):
        Action.__init__(self, *args, **kwargs)
        self.url = 'ws/yabish/submitjob'

    def process(self, args):
        params = {'name': self.name}
        for i,arg in enumerate(args):
            params['arg' + str(i)] = arg
        print 'Running your job on the server.'
        resp, json_response = self.yabi.post(self.url, params)
        decoded_resp = self.decode_json(json_response)
        if not decoded_resp['success']:
            raise errors.RemoteError(decoded_resp['msg'])
        return decoded_resp['workflow_id']

class Attach(Action, FileDownload):
    def __init__(self, *args, **kwargs):
        Action.__init__(self, *args, **kwargs)
        self.url = 'workflows/'

    def sleepgenerator(self):
        t = 1
        while True:
            yield 3
        while t < 30:
            yield t
            t *= 2
        while True:
            yield 30

    def get_workflow(self, workflow_id):
        url = self.url + str(workflow_id)
        resp, json_response = self.yabi.get(url)
        return self.decode_json(json_response)

    def process(self, args):
        assert len(args) == 1, "Workflow id should be passed in"
        gen = self.sleepgenerator()
        workflow_id = args[0]
        resp = {}
        status = ''
        while status.lower() not in ('complete', 'error'):
            try:
                resp = self.get_workflow(workflow_id)
                status = resp.get('status', '')
                time.sleep(gen.next())
            except KeyboardInterrupt:
                print
                print "Job %s current status is '%s'" % (workflow_id, status)
                sys.exit()
        if status.lower() == 'error':
            raise errors.RemoteError('Error running workflow')
            return

        stageout_dir = resp['json']['jobs'][-1]['stageout']

        self.recursive_download(stageout_dir)

        stdout = os.path.join(stageout_dir,'STDOUTT.txt')
        stderr = os.path.join(stageout_dir,'STDERR.txt')
        self.download_file(stdout, sys.stdout, ignore_404=True)
        self.download_file(stderr, sys.stderr, ignore_404=True)

    def recursive_download(self, uri):
        if not uri.endswith('/'):
            uri += '/'
        ls_url = 'ws/fs/ls'
        params = {'uri': uri, 'recurse': True}
        resp, json_response = self.yabi.get(ls_url, params)
        response = self.decode_json(json_response)
        base_path = urlparse.urlparse(uri).path
        rel_dirs = map(lambda x: x[len(base_path):], response)
        rel_dirs = filter(lambda x: x != '', rel_dirs)
        rel_files = [[d[len(base_path):] + f[0] for f in listing['files']] for d,listing in response.items()]
        # flatten the file list
        rel_files = [f for f in itertools.chain.from_iterable(rel_files)]
        rel_files = filter(lambda x: x not in ('STDERR.txt', 'STDOUT.txt'), rel_files)
        for d in rel_dirs:
            mkdir_p(d)
        for f in rel_files:
            self.download_file(uri+f, f)


class ForegroundRemoteAction(object):
    def __init__(self, *args, **kwargs):
        self.action = RemoteAction(*args, **kwargs)
        self.attacher = Attach(*args, **kwargs)

    def process(self, args):
        workflow_id = self.action.process(args)
        self.attacher.process([workflow_id])

class BackgroundRemoteAction(object):
    def __init__(self, *args, **kwargs):
        self.action = RemoteAction(*args, **kwargs)

    def process(self, args):
        workflow_id = self.action.process(args)
        print "Submitted. Workflow id: %s" % workflow_id

class Login(Action):
    def __init__(self, *args, **kwargs):
        Action.__init__(self, *args, **kwargs)
        self.url = 'wslogin'

    def map_args(self, args):
        return {'username': args[0], 'password': args[1]}

    def process(self, args):
        params = self.map_args(args)
        resp, json_response = self.yabi.post(self.url, params)
        return self.process_response(self.decode_json(json_response))

    def process_response(self, response):
        return response.get('success', False)

class Ls(Action):
    def __init__(self, *args, **kwargs):
        Action.__init__(self, *args, **kwargs)
        self.url = 'ws/fs/ls'

    def map_args(self, args):
        uri = ''
        if args:
            uri = args[0]
        return {'uri': uri}

    def process_response(self, response):
        lst = response.values()[0]
        dirs = lst['directories']
        files = lst['files']
        for d in dirs:
            dirname = d[0]
            if not dirname.endswith('/'):
                dirname += "/"
            print dirname
        for f in files:
            print f[0]

class Jobs(Action):
    def __init__(self, *args, **kwargs):
        Action.__init__(self, *args, **kwargs)
        self.url = 'workflows/datesearch'

    def map_args(self, args):
        if args and args[0]:
            start = args[0]
        else:
            start = time.strftime('%Y-%m-%d') 
        
        return {'start': start}

    def process_response(self, response):
        for job in response:
            print '%7d  %s  %10s  %s' % (job['id'], job['created_on'], job['status'].upper(), job['name'])

class Cp(Action, FileDownload):
    def __init__(self, *args, **kwargs):
        Action.__init__(self, *args, **kwargs)
        self.url = 'ws/fs/copy'

    def is_local_file(self, filename):
        return (filename.find(':') == -1)

    def process(self, args):
        src = args[0]
        src_filename = src.split('/')[-1]
        if len(args) > 1 and args[1]:
            dst = args[1]
        else:
            dst = src_filename

        if self.is_local_file(dst):
            if os.path.isdir(dst):
                dst = os.path.join(dst, src_filename)
            self.download_file(src, dst)
        else:
            params = {'src': src, 'dst': dst}
            self.yabi.get(self.url, params)

class Rm(Action):
    def __init__(self, *args, **kwargs):
        Action.__init__(self, *args, **kwargs)
        self.url = 'ws/fs/rm'

    def map_args(self, args):
        uri = args[0]
        return {'uri': uri}

    def process_response(self, response):
        pass

    def decode_json(self, response):
        return None


def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError, e: 
        if e.errno != errno.EEXIST:
            raise
