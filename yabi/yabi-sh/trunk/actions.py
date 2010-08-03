import time
from transport import UnauthorizedError

class Action(object):
    def __init__(self, yabi):
        self.yabi = yabi

    def process(self, args):
        params = self.map_args(args)
        json_response = self.yabi.get(self.url, params)
        import json
        map_response = json.loads(json_response)
        self.process_response(map_response)


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


