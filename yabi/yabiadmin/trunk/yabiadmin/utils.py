from django.utils import simplejson as json

def json_error(message):
    return json.dumps({'error':message})
