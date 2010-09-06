import time
import json
import os

class Action(object):
    def __init__(self, yabi):
        self.yabi = yabi

    def process(self, args):
        params = self.map_args(args)
        resp, json_response = self.yabi.get(self.url, params)
        self.process_response(self.decode_json(json_response))

    def decode_json(self, resp):
        return json.loads(resp)        


class LS(Action):
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

class PS(Action):
    def __init__(self, *args, **kwargs):
        Action.__init__(self, *args, **kwargs)
        self.url = 'workflows/tszabo/datesearch'

    def map_args(self, args):
        if args and args[0]:
            start = args[0]
        else:
            start = time.strftime('%Y-%m-%d') 
        
        return {'start': start}

    def process_response(self, response):
        for job in [j for j in response if j['status'].lower() in ('', 'running')]:
            print '%7d  %s  %s' % (job['id'], job['created_on'], job['name'])

class CP(Action):
    def __init__(self, *args, **kwargs):
        Action.__init__(self, *args, **kwargs)
        self.url = 'ws/fs/copy'
        self.get_url = 'ws/fs/get'

    def is_local_file(self, filename):
        return (filename.find(':') == -1)

    def download_file(self, uri, name):
        params = {'uri': uri}
        response, contents = self.yabi.get(self.get_url, params)
        with open(name, 'w') as f:
            f.write(contents)

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

class RM(Action):
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

